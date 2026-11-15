# SPDX-License-Identifier: GPL-3.0-or-later
# Copyleft 🄯 2026 ISL and contributors
"""MkDocs hooks that turn the GitHub Markdown in handbook/ into the website.

The files stay written for GitHub; only the built site changes:
- GitHub alerts (> [!TIP] ...) become Material admonitions with English titles.
- The disclaimer box that tools/disclaimer.py puts on every page is collapsed,
  with its warning and last-updated date kept in the visible title.
- Links that leave handbook/ (CHANGELOG, LICENSE, README, the PDF) point to
  GitHub; the Handbook Searcher is copied into the site under searcher/.
- Under "7. Student experiences" on every page a comment box is added
  (utterances, assets/comments.js, loaded only after a click): comments are stored
  as GitHub issue comments in this repository.
- Section titles in the navigation come from each section's README heading;
  the start page is called "Home".
"""
import posixpath
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GITHUB = "https://github.com/FreeXYZ-HalfPI/Hannover-Handbook-InternationalStudents"

ALERTS = {
    "NOTE": ("note", "Note"),
    "TIP": ("tip", "Tip"),
    "IMPORTANT": ("info", "Important"),
    "WARNING": ("warning", "Warning"),
    "CAUTION": ("danger", "Caution"),
}
ALERT = re.compile(r"^> \[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\][ \t]*\n((?:>.*\n?)*)", re.M)
DISCLAIMER = re.compile(r"<!-- disclaimer:start -->\n(.*?)<!-- disclaimer:end -->", re.S)
LINK = re.compile(r"(\]\()([^)\s#]+)(#[^)\s]*)?\)")


def _admonition(kind, body, collapsed=False, css=""):
    """Indent a blockquote body under an admonition; a leading ### line becomes its title."""
    lines = [re.sub(r"^> ?", "", line) for line in body.rstrip("\n").split("\n")]
    marker, title = ALERTS[kind]
    if lines and lines[0].startswith("### "):
        title = lines.pop(0)[4:].strip()
        while lines and not lines[0].strip():
            lines.pop(0)
    title = title.replace('"', "'")
    head = f'{"???" if collapsed else "!!!"} {marker}{" " + css if css else ""} "{title}"'
    return head + "\n" + "\n".join(("    " + line) if line.strip() else "" for line in lines) + "\n\n"


def _disclaimer(match):
    """First alert in the box: collapsed, titled with its warning and date. Others: as usual."""
    block = match.group(1)
    first = ALERT.search(block)
    if not first:
        return block
    body = first.group(2)
    lines = [re.sub(r"^> ?", "", line) for line in body.rstrip("\n").split("\n")]
    headings = [line[4:].strip() for line in lines if line.startswith("### ")]
    rest = [line for line in lines if not line.startswith("### ")]
    # Drop blank lines left where the headings were, but keep paragraph breaks.
    cleaned = []
    for line in rest:
        if line.strip() or (cleaned and cleaned[-1].strip()):
            cleaned.append(line)
    title_body = "### " + " · ".join(headings) + "\n" + "\n".join(cleaned)
    out = _admonition(first.group(1), title_body, collapsed=True, css="isl-disclaimer")
    return out + ALERT.sub(lambda m: _admonition(m.group(1), m.group(2)), block[first.end():])


def _outside_link(page, config):
    """Rewrite relative links that leave docs_dir to GitHub (or to the copied searcher)."""
    docs = Path(config["docs_dir"]).resolve()
    src_dir = posixpath.dirname(page.file.src_uri)

    def fix(match):
        target, anchor = match.group(2), match.group(3) or ""
        if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I) or target.startswith("/"):
            return match.group(0)
        full = (docs / src_dir / target).resolve()
        try:
            full.relative_to(docs)
            return match.group(0)
        except ValueError:
            pass
        rel = full.relative_to(ROOT).as_posix()
        if rel.startswith("search/"):
            url = config["site_url"].rstrip("/") + "/searcher/"
        elif rel.endswith(".pdf"):
            url = f"{GITHUB}/releases/latest/download/{rel.rsplit('/', 1)[-1]}"
        else:
            url = f"{GITHUB}/blob/main/{rel}"
        return f"{match.group(1)}{url}{anchor})"

    return fix


# --- Look and feel: home page hero, section cards, compact page header -------------
HERO = {'pdf': 'Hannover-Handbook-International-Students.pdf', 'home_start': '07-resources/54-checklist/', 'eyebrow': 'Leibniz University Hannover · for students from every country', 'title': 'Living in Hannover — A Practical Handbook', 'sub': 'for International Students', 'lead': 'A practical, step-by-step guide: every administrative task in order, with an official source and a review date.', 'start': 'Where do I start?', 'pdf_label': '📥 Download the PDF', 'pages': 'pages', 'sections': 'sections', 'free': 'free & copyleft', 'pagesword': 'pages', 'digits': False, 'cards_title': 'Sections'}
ICONS = {"01": "🧳", "02": "🎓", "03": "🏛️", "04": "🏠", "05": "💼", "06": "🤝", "07": "📚", "08": "🌍", "09": "📥"}
_cards = []


def _num(n):
    text = str(n)
    return text.translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")) if HERO["digits"] else text


META_KEYS = ("**تاریخ آخرین بررسی:**", "**Last reviewed:**")
LEGEND = re.compile(r" · (\*\*(?:راهنما|Key):\*\*.*)$")


def _meta_alert(kind, body):
    """The 'last reviewed / section / key' tip on every page becomes a quiet one-line header."""
    if kind != "TIP":
        return None
    lines = [re.sub(r"^> ?", "", line).strip() for line in body.rstrip("\n").split("\n")]
    text = " ".join(line for line in lines if line)
    if not text.startswith(META_KEYS):
        return None
    text = re.sub(r"(\d{4})-(\d{2})-(\d{2})", "\\1\u2011\\2\u2011\\3", text)  # dates must not break at the hyphens
    legend = LEGEND.search(text)
    meta = text[: legend.start()] if legend else text
    out = meta + "\n{: .isl-meta }\n\n"
    if legend:
        out += legend.group(1) + "\n{: .isl-legend }\n\n"
    return out


def _hero():
    pdf = f"{GITHUB}/releases/latest/download/{HERO['pdf']}"
    pages = sum(c[2] for c in _cards)
    cards = "".join(
        f'<a class="isl-card" href="{url}"><span class="isl-card__icon">{icon}</span>'
        f'<span class="isl-card__title">{title}</span>'
        f'<span class="isl-card__meta">{_num(count)} {HERO["pagesword"]}</span></a>'
        for title, url, count, icon in _cards
    )
    return (
        '<section class="isl-hero">'
        f'<p class="isl-hero__eyebrow">{HERO["eyebrow"]}</p>'
        f'<h1>{HERO["title"]}</h1>'
        f'<p class="isl-hero__sub" dir="ltr">{HERO["sub"]}</p>'
        f'<p class="isl-hero__lead">{HERO["lead"]}</p>'
        '<p class="isl-hero__actions">'
        f'<a class="md-button" href="{HERO["home_start"]}">{HERO["start"]}</a> '
        f'<a class="md-button md-button--ghost" href="{pdf}">{HERO["pdf_label"]}</a></p>'
        f'<p class="isl-hero__stats"><span><strong>{_num(pages)}</strong> {HERO["pages"]}</span>'
        f'<span><strong>{_num(len(_cards))}</strong> {HERO["sections"]}</span>'
        f'<span>{HERO["free"]}</span></p></section>'
        f'<h2 class="isl-cards-title" id="sections">{HERO["cards_title"]}</h2>'
        f'<div class="isl-cards">{cards}</div>'
    )


def on_page_markdown(markdown, page, config, files, **kwargs):
    markdown = DISCLAIMER.sub(_disclaimer, markdown)
    markdown = ALERT.sub(lambda m: _meta_alert(m.group(1), m.group(2)) or _admonition(m.group(1), m.group(2)), markdown)
    return LINK.sub(_outside_link(page, config), markdown)


EXPERIENCES = re.compile(r'<h2 id="[^"]*">\s*7\.\s*Student experiences.*?</h2>', re.S)

COMMENTS = """
<div class="isl-comments" id="isl-comments" data-repo="{repo}">
<p><strong>💬 Your experience or comment</strong></p>
<p>Write your experience, tip or correction about this page here. Your comment is <strong>public</strong> and appears under <strong>your GitHub username</strong> as a comment in the <a href="{github}/issues?q=is%3Aissue+label%3A%22%F0%9F%92%AC+comments%22">issues of this repository</a>; the team sees it. Do not post personal data (addresses, case or passport numbers) or identifying details on sensitive topics (consulate, military service, residence status). <a href="{github}/blob/main/COMMENTS.md">Comment rules</a>.</p>
<p><em>This section is unofficial: every comment is one person's experience, not law and not official advice. Please give the year and, if you can, the source.</em></p>
<p><button type="button" class="md-button md-button--primary isl-comments-load">💬 Show comments and write one</button><br><small>When you click, your browser connects to utteranc.es and GitHub; nothing is sent before that. A GitHub account is needed; without one, use the <a href="{form}">experience form</a>.</small></p>
<div class="isl-comments-box"></div>
<noscript><p>Comments need JavaScript; or use the <a href="{form}">experience form</a>.</p></noscript>
</div>
"""


def on_page_content(html, page, config, files, **kwargs):
    """The start page gets a hero and section cards; every page gets a comment box under its experiences."""
    if page.file.src_uri == "README.md":
        html = re.sub(r"<h1[^>]*>.*?</h1>", lambda m: _hero(), html, count=1, flags=re.S)
    heading = EXPERIENCES.search(html)
    if not heading:
        return html
    nxt = html.find("<h2", heading.end())
    cut = len(html) if nxt == -1 else nxt
    form = f"{GITHUB}/issues/new?template=experience.md&title=%5Bhandbook/{page.file.src_uri}%5D%20"
    box = COMMENTS.format(repo=GITHUB.split("github.com/")[1], github=GITHUB, form=form)
    return html[:cut] + box + html[cut:]


def on_nav(nav, config, files, **kwargs):
    """Name each section after its README heading, without the part in brackets."""
    docs = Path(config["docs_dir"])
    for item in nav.items:
        if item.is_page and item.file.src_uri == "README.md":
            item.title = "Home"
        if not item.is_section or not item.children:
            continue
        index = next((c for c in item.children if c.is_page and c.file.src_uri.endswith("README.md")), None)
        if index is None:
            continue
        folder = index.file.src_uri.split("/")[0][:2]
        count = len([c for c in item.children if c.is_page and not c.file.src_uri.endswith("README.md")])
        _cards.append([item.title, index.url, count, ICONS.get(folder, "📄")])
        first = (docs / index.file.src_uri).read_text(encoding="utf-8").split("\n", 1)[0]
        title = re.sub(r"\s*\(.*\)\s*$", "", first.lstrip("# ").strip())
        if title:
            item.title = title
            _cards[-1][0] = title
    return nav


def on_post_build(config, **kwargs):
    """The offline Handbook Searcher (search/) is served at searcher/ on the site."""
    shutil.copytree(ROOT / "search", Path(config["site_dir"]) / "searcher", dirs_exist_ok=True)
