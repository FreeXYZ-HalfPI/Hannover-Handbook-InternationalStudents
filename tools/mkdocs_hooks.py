# SPDX-License-Identifier: GPL-3.0-or-later
# Copyleft 🄯 2026 ISL and contributors
"""MkDocs hooks that turn the GitHub Markdown in handbook/ into the website.

The files stay written for GitHub; only the built site changes:
- GitHub alerts (> [!TIP] ...) become Material admonitions with English titles.
- The disclaimer box that tools/disclaimer.py puts on every page is collapsed,
  with its warning and last-updated date kept in the visible title.
- Links that leave handbook/ (CHANGELOG, LICENSE, README, the PDF) point to
  GitHub; the Handbook Searcher is copied into the site under searcher/.
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
            url = f"{GITHUB}/raw/main/{rel}"
        else:
            url = f"{GITHUB}/blob/main/{rel}"
        return f"{match.group(1)}{url}{anchor})"

    return fix


def on_page_markdown(markdown, page, config, files, **kwargs):
    markdown = DISCLAIMER.sub(_disclaimer, markdown)
    markdown = ALERT.sub(lambda m: _admonition(m.group(1), m.group(2)), markdown)
    return LINK.sub(_outside_link(page, config), markdown)


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
        first = (docs / index.file.src_uri).read_text(encoding="utf-8").split("\n", 1)[0]
        title = re.sub(r"\s*\(.*\)\s*$", "", first.lstrip("# ").strip())
        if title:
            item.title = title
    return nav


def on_post_build(config, **kwargs):
    """The offline Handbook Searcher (search/) is served at searcher/ on the site."""
    shutil.copytree(ROOT / "search", Path(config["site_dir"]) / "searcher", dirs_exist_ok=True)
