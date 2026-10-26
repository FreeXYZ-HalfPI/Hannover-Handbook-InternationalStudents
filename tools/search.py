"""Search both handbooks from the terminal.

Usage: python3 tools/search.py [--isl | --intl] [-n N] WORDS...

Reads the Markdown pages directly (this repository and the sibling handbook
repository, if it is checked out next to this one), so results are always
current. Uses the same matching as search/index.html: accents, Persian/Arabic
letters and digits are normalised, and English, German and Persian synonyms
are matched (e.g. "residence" also finds "Aufenthaltserlaubnis" and "اقامت").
"""
import argparse
import re
import sys

from build_search import collect, normalize

BOLD, DIM, RESET = ("\033[1m", "\033[2m", "\033[0m") if sys.stdout.isatty() else ("", "", "")


def plain(md):
    md = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", md)
    md = re.sub(r"\[!(TIP|NOTE|WARNING|IMPORTANT|CAUTION)\]", "", md)
    return re.sub(r"\s+", " ", re.sub(r"[*_`>#|]|-{3,}", " ", md)).strip()


def load_synonyms(groups):
    """Map every normalised term to its group; multi-word terms are also returned as phrases."""
    synonyms, phrases = {}, []
    for g in groups:
        norm = list(dict.fromkeys(w for w in (normalize(x) for x in g) if w))
        for w in norm:
            synonyms[w] = norm
            if " " in w:
                phrases.append(w)
    return synonyms, sorted(phrases, key=len, reverse=True)


def parse(query, synonyms, phrases):
    q, groups = f" {normalize(query)} ", []
    for ph in phrases:
        if f" {ph} " in q:
            groups.append((ph, [ph] + [s for s in synonyms[ph] if s != ph]))
            q = q.replace(f" {ph} ", " ", 1)
    words = q.split()
    if len(words) + len(groups) > 1:
        words = [w for w in words if len(w) > 1 or w.isdigit()]
    for w in words:
        alts = [w] + [s for s in synonyms.get(w, []) if s != w]
        groups.append((w, alts))
    return groups


def score(title, head, body, groups, phrase, require_all):
    total, matched = 0.0, 0
    for _, alts in groups:
        best = 0.0
        for k, alt in enumerate(alts):
            start = re.compile(rf"(^| ){re.escape(alt)}")
            # The typed word may match inside words (German compounds); synonyms only at a word start.
            if k == 0:
                s = (8 if alt in title else 0) + (5 if alt in head else 0) + min(body.count(alt), 5)
                if s and any(start.search(x) for x in (title, head, body)):
                    s *= 1.25
            else:
                s = ((8 if start.search(title) else 0) + (5 if start.search(head) else 0)
                     + min(len(start.findall(body)), 5)) * 0.7
            best = max(best, s)
        if best:
            matched += 1
            total += best
        elif require_all:
            return 0
    if not matched:
        return 0
    if len(groups) > 1 and any(phrase in x for x in (body, head, title)):
        total += 12
    return total * matched / len(groups)


def snippet(text, words, width=200):
    low = text.lower()
    hits = [low.find(w) for w in words if low.find(w) >= 0]
    start = max(0, min(hits) - 60) if hits else 0
    part = text[start:start + width]
    return ("… " if start else "") + part + (" …" if start + width < len(text) else "")


def main():
    ap = argparse.ArgumentParser(description="Search both Hannover handbooks.")
    ap.add_argument("words", nargs="+")
    ap.add_argument("-n", type=int, default=8, help="number of pages to show (default 8)")
    group = ap.add_mutually_exclusive_group()
    group.add_argument("--isl", action="store_true", help="only the Persian ISL handbook")
    group.add_argument("--intl", action="store_true", help="only the English handbook")
    args = ap.parse_args()

    index = collect()
    synonyms, phrases = load_synonyms(index["synonyms"])
    query = " ".join(args.words)
    groups = parse(query, synonyms, phrases)
    if not groups:
        sys.exit("Please give at least one word to search for.")
    phrase = " ".join(w for w, _ in groups)
    only = "isl" if args.isl else "intl" if args.intl else None

    rows = []
    for p, heading, anchor, md in index["items"]:
        page = index["pages"][p]
        hb = index["handbooks"][page["h"]]
        if only and hb["id"] != only:
            continue
        text = plain(md)
        rows.append((page, hb, heading, anchor, text,
                     normalize(f"{page['n']} {page['t']}"), normalize(heading), normalize(text)))

    def run(require_all):
        out = {}
        for row in rows:
            s = score(row[5], row[6], row[7], groups, phrase, require_all)
            if s:
                out.setdefault(id(row[0]), []).append((s, row))
        return out

    by_page = run(True) or (run(False) if len(groups) > 1 else {})
    if not by_page:
        print(f"Nothing found for “{query}”. Try fewer or other words — German terms often work best.")
        return
    ranked = sorted(by_page.values(), key=lambda hits: -(max(h[0] for h in hits) + 0.15 * (sum(h[0] for h in hits) - max(h[0] for h in hits))))
    words = sorted({a for _, alts in groups for a in alts}, key=len, reverse=True)
    print(f"{len(by_page)} page(s) for “{query}”\n")
    for hits in ranked[:args.n]:
        hits.sort(key=lambda h: -h[0])
        page, hb = hits[0][1][0], hits[0][1][1]
        print(f"{BOLD}{page['t']}{RESET}  {DIM}[{hb['short']}]{RESET}")
        for _, (_, _, heading, anchor, text, *_rest) in hits[:2]:
            print(f"  › {heading or page['t']}")
            print(f"    {DIM}{snippet(text, words)}{RESET}")
            print(f"    {hb['url']}{page['p']}#{anchor}")
        print()


if __name__ == "__main__":
    main()
