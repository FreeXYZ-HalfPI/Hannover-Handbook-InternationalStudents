# SPDX-License-Identifier: GPL-3.0-or-later
# Copyleft 🄯 2026 ISL and contributors
"""Build the search index used by search/index.html and tools/search.py.

Usage: python3 tools/build_search.py [PATH_TO_OTHER_HANDBOOK_REPO ...]

Indexes the topic pages of this repository and of every sibling handbook
repository it can find (Hannover-Handbook-ISL and
Hannover-Handbook-InternationalStudents checked out next to this one, or the
paths given as arguments), so one search covers both handbooks.
Writes search/search-index.js. The same file is used in both repositories.
"""
import json
import re
import subprocess
import sys
import unicodedata
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "search" / "search-index.js"

HANDBOOKS = {
    "Hannover-Handbook-ISL": {
        "id": "isl", "lang": "fa", "dir": "rtl",
        "name": "کتابچه ISL (فارسی)", "short": "ISL · فارسی",
        "url": "https://github.com/FreeXYZ-HalfPI/Hannover-Handbook-ISL/blob/main/",
    },
    "Hannover-Handbook-InternationalStudents": {
        "id": "intl", "lang": "en", "dir": "ltr",
        "name": "International Students Handbook (English)", "short": "International · English",
        "url": "https://github.com/FreeXYZ-HalfPI/Hannover-Handbook-InternationalStudents/blob/main/",
    },
}

# Words that mean the same thing in English, German and Persian. A query word
# that equals one of them also finds the others, so an English search reaches
# the Persian handbook and the other way round. Multi-word entries are matched
# as phrases in the query ("residence permit" counts as one term).
SYNONYMS = [
    ["anmeldung", "registration", "register", "address registration", "ثبت محل سکونت", "meldebescheinigung", "ثبت", "ملده", "بورگرامت", "bürgeramt"],
    ["aufenthaltserlaubnis", "residence", "residence permit", "aufenthaltstitel", "اقامت", "اجازه اقامت", "ausländerbehörde", "fiktionsbescheinigung"],
    ["visa", "visum", "ویزا", "روادید"],
    ["insurance", "health insurance", "versicherung", "krankenversicherung", "krankenkasse", "بیمه", "بیمه درمانی"],
    ["bank", "konto", "account", "حساب", "بانک", "basiskonto"],
    ["sperrkonto", "blocked account", "مسدودی", "حساب مسدودی"],
    ["housing", "accommodation", "wohnung", "wohnheim", "room", "flat", "shared flat", "student residence", "مسکن", "خوابگاه", "خانه", "اتاق", "wg"],
    ["rent", "miete", "اجاره", "kaution", "deposit", "ودیعه"],
    ["job", "work", "arbeit", "student job", "werkstudent", "minijob", "hiwi", "کار", "شغل", "کار دانشجویی"],
    ["tax", "steuer", "steuererklärung", "tax id", "steuer id", "مالیات", "شماره مالیاتی"],
    ["doctor", "arzt", "hausarzt", "family doctor", "پزشک", "دکتر", "پزشک خانواده"],
    ["dentist", "zahnarzt", "dental", "دندان", "دندان‌پزشک", "دندان‌پزشکی"],
    ["pharmacy", "apotheke", "داروخانه", "medicine", "دارو"],
    ["exam", "exams", "prüfung", "prüfungen", "exam registration", "امتحان", "امتحانات", "qis"],
    ["semester fee", "semesterbeitrag", "rückmeldung", "re registration", "شهریه", "هزینه ترم"],
    ["ticket", "semester ticket", "semesterticket", "deutschlandticket", "deutschlandsemesterticket", "بلیت", "بلیت ترم"],
    ["transport", "public transport", "bus", "tram", "üstra", "حمل و نقل", "اتوبوس", "مترو"],
    ["german", "deutsch", "آلمانی", "dsh", "testdaf"],
    ["language", "sprache", "زبان", "llc"],
    ["emergency", "notfall", "notaufnahme", "emergency number", "اورژانس", "اضطراری"],
    ["police", "polizei", "پلیس"],
    ["scholarship", "stipendium", "بورسیه", "funding"],
    ["passport", "reisepass", "pass", "پاسپورت", "گذرنامه"],
    ["translation", "übersetzung", "translator", "ترجمه", "مترجم"],
    ["certified", "beglaubigung", "beglaubigt", "برابر"],
    ["family", "familie", "spouse", "خانواده", "همسر", "children", "فرزند"],
    ["mensa", "canteen", "food", "غذاخوری", "غذا"],
    ["library", "bibliothek", "tib", "کتابخانه"],
    ["legal", "lawyer", "legal advice", "legal clinic", "anwalt", "rechtsberatung", "حقوقی", "وکیل", "مشاوره حقوقی"],
    ["contract", "vertrag", "قرارداد", "kündigung", "فسخ"],
    ["scam", "fraud", "betrug", "کلاهبرداری"],
    ["counselling", "counseling", "beratung", "مشاوره", "ptb"],
    ["mental", "psychological", "psychotherapy", "روان", "روانی"],
    ["driving licence", "driving license", "führerschein", "گواهینامه", "گواهینامه رانندگی"],
    ["graduation", "abschluss", "graduate", "after graduation", "فارغ التحصیلی", "فارغالتحصیلی"],
    ["deadline", "frist", "deadlines", "مهلت", "calendar", "تقویم"],
    ["enrolment", "enrollment", "immatrikulation", "einschreibung", "ثبت‌نام"],
    ["application", "bewerbung", "uni assist", "پذیرش"],
    ["sim", "sim card", "handy", "mobile", "internet", "سیم‌کارت", "اینترنت"],
    ["broadcasting", "rundfunkbeitrag", "gez"],
    ["waste", "müll", "trash", "زباله"],
    ["sports", "sport", "hochschulsport", "ورزش"],
    ["holiday", "feiertag", "تعطیلات", "تعطیل"],
    ["strike", "streik", "اعتصاب"],
    ["sick note", "krankmeldung", "arbeitsunfähigkeitsbescheinigung", "گواهی بیماری"],
    ["iranian", "iran", "ایران", "ایرانی"],
]

PERSIAN_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
ARABIC_TO_PERSIAN = str.maketrans({"ي": "ی", "ى": "ی", "ك": "ک", "ة": "ه", "‌": "", "‍": "", "ـ": ""})


def normalize(text):
    """Lower-case, strip accents and diacritics, unify Persian/Arabic letters and digits.

    search/index.html implements the same steps in JavaScript (norm()).
    """
    text = text.translate(ARABIC_TO_PERSIAN).translate(PERSIAN_DIGITS)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = text.lower().replace("ß", "ss")
    return re.sub(r"[^\w]+", " ", text).strip()


def slug(heading, seen):
    """GitHub's heading anchor: lower-case, keep letters/marks/numbers/_/-/space, spaces to '-'."""
    s = "".join(c for c in heading.lower() if unicodedata.category(c)[0] in "LMN" or c in "_- ")
    s = s.replace(" ", "-")
    n = seen.get(s, 0)
    seen[s] = n + 1
    return s if n == 0 else f"{s}-{n}"


def plain_heading(md):
    """Heading text as GitHub renders it (without markup and link targets)."""
    md = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", md)
    return re.sub(r"[*_`]", "", md).strip()


# Boilerplate repeated on every page (review dates, attribution, standard
# disclaimers, empty experience lists) would match many queries; leave it out.
NOISE = re.compile(r"^> (\[!TIP\]|\*\*Last reviewed|\*\*تاریخ آخرین بررسی|تهیه و تنظیم|\*Iran|\*Iranische"
                   r"|This section is for personal experiences|این بخش برای تجربه‌های شخصی"
                   r"|This page is general information, not legal advice\.?$|این صفحه اطلاعات عمومی است و مشاوره حقوقی به شمار نمی‌آید\.?$)"
                   r"|^>\s*$|^---\s*$|^- (No experiences added yet\.|هنوز تجربه‌ای ثبت نشده است\.)$")
EMPTY_ALERT = re.compile(r"^> \[!\w+\]\s*\n?(?!>)", re.M)
SOURCES = re.compile(r"^(6|۶)\.\s")


def sections(path):
    """Split a page into (heading, anchor, markdown) chunks at ## and ### headings.

    The sources table (section 6) is left out: it only repeats the links.
    """
    # The disclaimer box (tools/disclaimer.py) is the same on every page.
    text = re.sub(r"<!-- disclaimer:start -->.*?<!-- disclaimer:end -->", "", path.read_text(encoding="utf-8"), flags=re.S)
    lines = text.splitlines()
    seen, chunks, title = {}, [], path.stem
    heading, anchor, body, fence = None, "", [], False
    for line in lines:
        if line.startswith("```"):
            fence = not fence
        m = None if fence else re.match(r"^(#{1,3})\s+(.*)$", line)
        if m:
            text = plain_heading(m.group(2))
            if heading is not None or body:
                chunks.append((heading, anchor, body))
            if m.group(1) == "#":
                title, heading, anchor = text, "", slug(text, seen)
            else:
                heading, anchor = text, slug(text, seen)
            body = []
            continue
        if not NOISE.match(line):
            body.append(line)
    chunks.append((heading, anchor, body))
    out = []
    for heading, anchor, body in chunks:
        md = EMPTY_ALERT.sub("", "\n".join(body)).strip()
        if heading is None or SOURCES.match(heading or "") or not md:
            continue
        out.extend((heading, anchor, part) for part in split(md))
    return title, out


def split(md, limit=1200, target=600):
    """Cut a section longer than `limit` into pieces of about `target` characters.

    Pieces are whole paragraphs, top-level list items (with their sub-items) and
    tables. Small pieces rank better (a long FAQ section would otherwise match
    every query) and show the reader the paragraph that answers the question.
    """
    if len(md) <= limit:
        return [md]
    blocks, cur = [], []
    for line in md.split("\n"):
        starts_item = re.match(r"^(\d+\.|[-*])\s", line)
        if not line.strip() or (starts_item and cur):
            if cur:
                blocks.append("\n".join(cur))
            cur = [line] if line.strip() else []
        else:
            cur.append(line)
    if cur:
        blocks.append("\n".join(cur))
    parts, cur = [], ""
    for b in blocks:
        if cur and len(cur) + len(b) > target:
            parts.append(cur.strip())
            cur = ""
        cur += b + "\n\n"
    if cur.strip():
        parts.append(cur.strip())
    return parts


def repo_name(root):
    try:
        url = subprocess.run(["git", "-C", str(root), "remote", "get-url", "origin"],
                             capture_output=True, text=True, check=True).stdout.strip()
        return url.rstrip("/").removesuffix(".git").rsplit("/", 1)[-1]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return root.name


def find_repos(extra):
    repos = [ROOT] + [Path(p).resolve() for p in extra]
    for name in HANDBOOKS:
        sibling = ROOT.parent / name
        if (sibling / "handbook").is_dir():
            repos.append(sibling.resolve())
    unique = []
    for r in repos:
        if r not in unique and (r / "handbook").is_dir():
            unique.append(r)
    return unique


def collect(extra=()):
    """Return the index as a dict: handbooks, pages and section items."""
    index = {"built": date.today().isoformat(), "handbooks": [], "pages": [], "items": [], "synonyms": SYNONYMS}
    for repo in find_repos(extra):
        meta = HANDBOOKS.get(repo_name(repo)) or HANDBOOKS.get(repo.name)
        if not meta or any(h["id"] == meta["id"] for h in index["handbooks"]):
            continue
        h = len(index["handbooks"])
        index["handbooks"].append(meta)
        for page in sorted((repo / "handbook").glob("*/[0-9][0-9]-*.md")):
            readme = page.parent / "README.md"
            section = readme.read_text(encoding="utf-8").splitlines()[0].lstrip("# ").strip() if readme.exists() else ""
            title, chunks = sections(page)
            p = len(index["pages"])
            index["pages"].append({"h": h, "n": int(page.name[:2]), "t": title, "s": section,
                                   "p": page.relative_to(repo).as_posix()})
            for heading, anchor, md in chunks:
                index["items"].append([p, heading, anchor, md])
    return index


def main():
    index = collect(sys.argv[1:])
    OUT.parent.mkdir(exist_ok=True)
    data = json.dumps(index, ensure_ascii=False, separators=(",", ":"))
    OUT.write_text("// Generated by tools/build_search.py — do not edit by hand.\n"
                   f"window.HANDBOOK_SEARCH = {data};\n", encoding="utf-8")
    names = ", ".join(f"{h['id']} ({sum(1 for p in index['pages'] if index['handbooks'][p['h']] is h)} pages)"
                      for h in index["handbooks"])
    print(f"wrote {OUT.relative_to(ROOT)}: {len(index['items'])} sections from {names}")


if __name__ == "__main__":
    main()
