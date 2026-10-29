# SPDX-License-Identifier: GPL-3.0-or-later
# Copyleft 🄯 2026 ISL and contributors
"""Insert or refresh the disclaimer box at the top of every handbook page.

Usage: python3 tools/disclaimer.py

Each page gets a large red box saying the handbook is guidance based on
students' experience, that rules can change, and that ISL takes no
responsibility for the content being up to date, followed by the page's last
update date in large type. Pages about health also get a medical disclaimer.
Each box ends with one-click links that open a GitHub issue (error, idea or
experience) with the page's path already in the title, or the page's editor.
Run it after changing a page's "last reviewed" date; the box sits between
<!-- disclaimer:start --> and <!-- disclaimer:end --> and is rewritten each time.
The same file is used in both handbook repositories; the language follows the
page (Persian or English).
"""
import re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
HANDBOOK = ROOT / "handbook"
START, END = "<!-- disclaimer:start -->", "<!-- disclaimer:end -->"
BLOCK = re.compile(re.escape(START) + r".*?" + re.escape(END) + r"\n*", re.S)
DATE = re.compile(r"(?:Last reviewed:\*\*|تاریخ آخرین بررسی:\*\*|last reviewed: |تاریخ آخرین بررسی کل کتابچه: )\s*(\d{4}-\d{2}-\d{2})")

# Pages about health, by file name without the number.
MEDICAL = {"health-insurance", "counselling", "doctor-pharmacy", "emergency", "persian-speaking-doctors"}

TEXT = {
    "fa": {
        "title": "⚠️ این کتابچه فقط راهنما و حاصل تجربه دانشجویان است — نه قانون و نه مشاوره رسمی",
        "body": ("**قوانین، مبالغ، مهلت‌ها و روندهای اداری ممکن است هر زمان و بدون اطلاع قبلی تغییر کنند.** "
                 "انجمن دانشجویان ایرانی دانشگاه لایبنیتس هانوفر (ISL) و نویسندگان این کتابچه **هیچ مسئولیتی** "
                 "در قبال درستی، کامل بودن یا به‌روز بودن مطالب و پیامد استفاده از آن‌ها ندارند. "
                 "پیش از هر اقدام، اطلاعات را از نهاد رسمی مسئول بپرسید؛ ملاک نهایی همیشه همان نهاد است."),
        "date_page": "🗓️ آخرین به‌روزرسانی این صفحه: {date}",
        "date_index": "🗓️ آخرین به‌روزرسانی: {date}",
        "follow": "از تغییرات بعدی باخبر شوید: [فهرست تغییرات (CHANGELOG)]({changelog}) · در GitHub روی **Watch** بزنید · [کانال تلگرام ISL](https://t.me/hannover_iranian_students)",
        "copyleft": "کپی‌لفت 🄯 ISL و مشارکت‌کنندگان — آزاد برای استفاده، پخش و تغییر، به شرط انتشار با همین مجوز ([GNU GPL نسخه ۳ یا بالاتر]({license}))",
        "feedback": "💬 درباره این صفحه: [🐞 گزارش خطا یا پیوند خراب]({error}) · [💡 پیشنهاد یا ایده]({idea}) · [✍️ ثبت تجربه]({experience}) · [✏️ ویرایش مستقیم]({edit})",
        "med_title": "🩺 سلب مسئولیت پزشکی",
        "med_body": ("این صفحه **توصیه پزشکی، تشخیص یا درمان نیست** و جای معاینه و مشاوره پزشک، روان‌درمانگر یا داروساز را نمی‌گیرد. "
                     "درباره بیماری، دارو و درمان فقط با پزشک یا داروساز تصمیم بگیرید. "
                     "**در وضعیت اضطراری فوراً با 112 تماس بگیرید**؛ بیرون از ساعت مطب‌ها: 116117. "
                     "نام پزشکان یا مراکز درمانی (اگر آمده باشد) از فهرست‌های عمومی گرفته شده و به معنای توصیه، تأیید یا تضمین ISL نیست."),
    },
    "en": {
        "title": "⚠️ This handbook is guidance based on students' experience — not law and not official advice",
        "body": ("**Rules, amounts, deadlines and procedures can change at any time without notice.** "
                 "The Iranian Student Association of Leibniz University Hannover (ISL) and the authors of this handbook "
                 "accept **no responsibility** for the accuracy, completeness or currency of the content, or for the "
                 "consequences of using it. Check with the responsible official office before you act; it always has the final word."),
        "date_page": "🗓️ This page was last updated: {date}",
        "date_index": "🗓️ Last updated: {date}",
        "follow": "Stay informed about changes: [changelog]({changelog}) · click **Watch** on GitHub · [ISL Telegram channel](https://t.me/hannover_iranian_students)",
        "copyleft": "Copyleft 🄯 ISL and contributors — free to use, share and change, as long as it stays under the same license ([GNU GPL v3 or later]({license}))",
        "feedback": "💬 About this page: [🐞 Report an error or broken link]({error}) · [💡 Suggest an idea]({idea}) · [✍️ Share an experience]({experience}) · [✏️ Edit it yourself]({edit})",
        "med_title": "🩺 Medical disclaimer",
        "med_body": ("This page is **not medical advice, diagnosis or treatment** and does not replace an examination or advice "
                     "from a doctor, psychotherapist or pharmacist. Make decisions about illness, medicines and treatment only with them. "
                     "**In an emergency call 112 immediately**; outside surgery hours call 116117. "
                     "Names of doctors or clinics (where given) come from public registers and are not a recommendation, endorsement or guarantee by ISL."),
    },
}

# The Persian handbook writes its review dates in Persian.
LANG = "fa" if "تاریخ آخرین بررسی" in (HANDBOOK / "README.md").read_text(encoding="utf-8") else "en"
GITHUB = "https://github.com/FreeXYZ-HalfPI/" + ("Hannover-Handbook-ISL" if LANG == "fa" else "Hannover-Handbook-InternationalStudents")


def feedback_links(page):
    """Issue links that open the right template with the page path in the title."""
    def issue(template):
        return f"{GITHUB}/issues/new?template={template}&title={quote(f'[{page}] ')}"
    return {"error": issue("broken-link-or-error.md"), "idea": issue("idea.md"),
            "experience": issue("experience.md"), "edit": f"{GITHUB}/edit/main/{page}"}


def box(lang, date, changelog, medical, index, page):
    t = TEXT[lang]
    # Isolate the date as left-to-right, or Persian text around it reverses it to 25-10-2026.
    when = (t["date_index"] if index else t["date_page"]).format(date=f"\u2066{date}\u2069")
    lines = [START, "> [!CAUTION]", f"> ### {t['title']}", ">", f"> {t['body']}", ">",
             f"> ### {when}", ">", f"> {t['follow'].format(changelog=changelog)}", ">",
             f"> {t['copyleft'].format(license=changelog.replace('CHANGELOG.md', 'LICENSE'))}", ">",
             f"> {t['feedback'].format(**feedback_links(page))}"]
    if medical:
        lines += ["", "> [!WARNING]", f"> ### {t['med_title']}", ">", f"> {t['med_body']}"]
    return "\n".join(lines + [END]) + "\n\n"


def page_date(text):
    m = DATE.search(text)
    return m.group(1) if m else None



def apply(path, date, medical=False, index=False):
    text = BLOCK.sub("", path.read_text(encoding="utf-8"))
    changelog = Path("../" * len(path.parent.relative_to(ROOT).parts)) / "CHANGELOG.md"
    head, _, rest = text.partition("\n")
    new = head + "\n\n" + box(LANG, date, changelog.as_posix(), medical, index, path.relative_to(ROOT).as_posix()) + rest.lstrip("\n")
    if new != path.read_text(encoding="utf-8"):
        path.write_text(new, encoding="utf-8")
        return True
    return False


def main():
    changed, latest_all = 0, ""
    for section in sorted(p for p in HANDBOOK.iterdir() if p.is_dir()):
        latest = ""
        for page in sorted(section.glob("[0-9][0-9]-*.md")):
            date = page_date(page.read_text(encoding="utf-8"))
            if not date:
                print(f"skipped {page.relative_to(ROOT)}: no review date")
                continue
            latest = max(latest, date)
            changed += apply(page, date, medical=page.stem[3:] in MEDICAL)
        if latest and (section / "README.md").exists():
            changed += apply(section / "README.md", latest, index=True)
        latest_all = max(latest_all, latest)
    changed += apply(HANDBOOK / "README.md", latest_all, index=True)
    print(f"updated {changed} files (handbook last updated {latest_all})")


if __name__ == "__main__":
    main()
