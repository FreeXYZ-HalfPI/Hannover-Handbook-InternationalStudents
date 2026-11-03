# SPDX-License-Identifier: GPL-3.0-or-later
# Copyleft 🄯 2026 ISL and contributors
"""Re-check the handbook's links and record the results in the pages.

Usage: python3 tools/refresh.py [--build]

1. Runs tools/check_links.sh, which writes link-report.tsv.
2. Sets the access date ("تاریخ دسترسی" / "Accessed") to today on every
   source row marked ✅ whose links all answered 200 in step 1.
3. Sets the page's review date (the "تاریخ آخرین بررسی" / "Last reviewed"
   line) to today on every page whose rows changed.
4. Runs tools/disclaimer.py, so the box at the top of each page and the
   section and index dates follow the review dates.
5. With --build: rebuilds search/search-index.js and the PDF.

Rows that do not answer 200 keep their old date and status, so a broken
link is never marked as checked.
"""
import datetime
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TODAY = datetime.date.today().isoformat()
DATE = r"\d{4}-\d{2}-\d{2}"
# The review date line in each page: Persian (ISL) or English (International Students).
REVIEW = re.compile(r"((?:تاریخ آخرین بررسی:\*\*|\*\*Last reviewed:\*\*)\s*)(" + DATE + ")")
URL = re.compile(r"https?://[^)\s|\"<>]+")
ACCESS = re.compile(DATE)


def run(cmd):
    subprocess.run(cmd, cwd=ROOT, check=True)


def ok_urls():
    ok = set()
    for line in (ROOT / "link-report.tsv").read_text(encoding="utf-8").splitlines():
        cols = line.split("\t")
        if cols[0] == "200":
            ok.add(cols[2])
    return ok


def update_row(line, ok):
    """Set the access date on a ✅ row when every link on it answered 200."""
    if not line.startswith("|") or "✅" not in line or not ACCESS.search(line):
        return line, False
    urls = [u.rstrip(".,;:") for u in URL.findall(line)]
    if not urls or any(u not in ok for u in urls):
        return line, False
    new = ACCESS.sub(TODAY, line, count=1)
    return new, new != line


def refresh_pages(ok):
    changed = 0
    for page in sorted((ROOT / "handbook").rglob("*.md")):
        text = page.read_text(encoding="utf-8")
        lines, touched = [], False
        for line in text.split("\n"):
            new, did = update_row(line, ok)
            lines.append(new)
            touched |= did
        if not touched:
            continue
        body = "\n".join(lines)
        body = REVIEW.sub(lambda m: m.group(1) + TODAY, body, count=1)
        page.write_text(body, encoding="utf-8")
        changed += 1
    return changed


def main():
    build = "--build" in sys.argv
    run(["bash", "tools/check_links.sh"])
    ok = ok_urls()
    print(f"{len(ok)} links answered 200")
    print(f"pages with updated source rows: {refresh_pages(ok)}")
    sys.path.insert(0, str(ROOT / "tools"))
    import disclaimer
    disclaimer.main()
    if build:
        run([sys.executable, "tools/build_search.py"])
        run([sys.executable, "tools/build_pdf.py"])


if __name__ == "__main__":
    main()
