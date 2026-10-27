# SPDX-License-Identifier: GPL-3.0-or-later
# Copyleft 🄯 2026 ISL and contributors
"""Regenerate section 6 (sources table) and section 7 (experiences) of every topic page.

Usage: bash tools/check_links.sh && python3 tools/build_sources.py [YYYY-MM-DD]

Section 6 lists every external link used on the page, in order of first use,
with its publisher, the access date and the result from link-report.tsv.
Section 7 is kept if it already contains experiences.
"""
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
HANDBOOK = ROOT / "handbook"
REPORT = ROOT / "link-report.tsv"

PUBLISHERS = {
    "uni-hannover.de": "Leibniz University Hannover",
    "lu-h.de": "Leibniz University Hannover",
    "tib.eu": "TIB – Leibniz Information Centre",
    "studentenwerk-hannover.de": "Studentenwerk Hannover",
    "stwh-portal.de": "Studentenwerk Hannover",
    "asta-hannover.de": "AStA Hannover",
    "hochschulsport-hannover.de": "Hochschulsport Hannover",
    "hannover.de": "City and Region of Hannover",
    "hannover.gov.de": "City of Hannover",
    "aha-region.de": "aha – Region Hannover waste management",
    "uestra.de": "ÜSTRA / GVH",
    "hannover-airport.de": "Hannover Airport",
    "staatstheater-hannover.de": "Staatstheater Hannover",
    "vhs-hannover.de": "Volkshochschule Hannover",
    "pd-h.polizei-nds.de": "Police Hannover",
    "hannonetz.de": "City of Hannover",
    "starting-business.de": "hannoverimpuls / LUH",
    "gesetze-im-internet.de": "Federal Ministry of Justice (law text)",
    "diplo.de": "Federal Foreign Office (German mission)",
    "auswaertiges-amt.de": "Federal Foreign Office",
    "make-it-in-germany.com": "Federal Government – Make it in Germany",
    "anerkennung-in-deutschland.de": "Federal Government – Recognition in Germany",
    "bundesregierung.de": "Federal Government",
    "bundesfinanzministerium.de": "Federal Ministry of Finance",
    "bundesgesundheitsministerium.de": "Federal Ministry of Health",
    "bundesumweltministerium.de": "Federal Environment Ministry",
    "bmi.bund.de": "Federal Ministry of the Interior",
    "bzst.de": "Federal Central Tax Office",
    "bundesnetzagentur.de": "Federal Network Agency",
    "bundesbank.de": "Deutsche Bundesbank",
    "bafin.de": "BaFin",
    "bafa.de": "Federal Office for Economic Affairs and Export Control",
    "bfarm.de": "Federal Institute for Drugs and Medical Devices",
    "bbk.bund.de": "Federal Office of Civil Protection",
    "zoll.de": "German Customs",
    "arbeitsagentur.de": "Federal Employment Agency",
    "deutsche-rentenversicherung.de": "Deutsche Rentenversicherung",
    "antidiskriminierungsstelle.de": "Federal Anti-Discrimination Agency",
    "elster.de": "German tax administration (ELSTER)",
    "lstn.niedersachsen.de": "Lower Saxony tax administration",
    "rundfunkbeitrag.de": "ARD ZDF Deutschlandradio Beitragsservice",
    "116117.de": "Kassenärztliche Bundesvereinigung",
    "dvka.de": "DVKA (GKV-Spitzenverband)",
    "uni-assist.de": "uni-assist",
    "anabin.kmk.org": "KMK",
    "zab.kmk.org": "KMK / ZAB",
    "daad.de": "DAAD",
    "study-in-germany.de": "DAAD",
    "aps.org.cn": "APS China (German Embassy / DAAD)",
    "aps-india.de": "APS India (German Embassy / DAAD)",
    "europa.eu": "European Union",
    "sanctionsmap.eu": "European Union",
    "verbraucherzentrale.de": "Verbraucherzentrale",
    "verbraucherzentrale-niedersachsen.de": "Verbraucherzentrale Niedersachsen",
    "telefonseelsorge.de": "TelefonSeelsorge",
    "hilfetelefon.de": "Federal Office for Family Affairs",
    "aponet.de": "ABDA (pharmacists)",
    "tk.de": "Techniker Krankenkasse",
    "aok.de": "AOK",
    "barmer.de": "BARMER",
    "ptb.uni-hannover.de": "ptb – psychological counselling",
    "llc.uni-hannover.de": "Leibniz Language Centre",
    "zqs.uni-hannover.de": "ZQS, Leibniz University Hannover",
}
UNOFFICIAL = ("fintiba.com", "gesetzlichekrankenkassen.de", "betanet.de", "iww.de", "asyl.net", "intl.kit.edu",
              "wiesbaden.de", "muenchen.de")


def publisher(url):
    host = urlparse(url).hostname or ""
    host = host.removeprefix("www.")
    for domain in sorted(PUBLISHERS, key=len, reverse=True):
        if host == domain or host.endswith("." + domain):
            return PUBLISHERS[domain]
    return host


def load_report():
    status = {}
    if REPORT.exists():
        for line in REPORT.read_text(encoding="utf-8").splitlines():
            parts = line.split("\t")
            if len(parts) >= 3:
                status[parts[2]] = parts[0]
    return status


def result(code):
    if code == "200":
        return "✅ Opened"
    if code in ("400", "403", "429", "500", "999") or code.startswith("3"):
        return "⚠️ Blocks automated checks — open in a browser"
    if code == "404":
        return "❌ Not found (404)"
    if code == "000":
        return "❌ No response on access date"
    return f"⚠️ Not checked ({code})" if code else "⚠️ Not checked"


FOOTER_7 = """## 7. Student experiences (unofficial)

> [!NOTE]
> This section is for personal experiences; it is not a general rule or legal advice. Share yours (with a date) on [page 57](../07-resources/57-contribute-experiences.md) or by opening a GitHub issue.

- No experiences added yet.
"""


def build(path, status, accessed):
    text = path.read_text(encoding="utf-8")
    if "<!-- footer -->" in text:
        body, experiences = text.split("<!-- footer -->")[0], None
    elif "\n## 6. Sources and official links" in text:
        body, rest = text.split("\n## 6. Sources and official links", 1)
        body += "\n"
        experiences = rest.split("\n## 7.", 1)[1] if "\n## 7." in rest else None
    else:
        return False
    links, labels = [], {}
    for label, url in re.findall(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", body):
        if url not in labels:
            links.append(url)
            labels[url] = label
        elif len(label) > len(labels[url]) and not label.startswith("http"):
            labels[url] = label
    rows = []
    for i, url in enumerate(links, 1):
        label = labels[url].replace("|", "\\|")
        pub = publisher(url)
        if any(d in url for d in UNOFFICIAL):
            pub += " — unofficial / secondary source"
        rows.append(f"| {i} | [{label}]({url}) | {pub} | {accessed} | {result(status.get(url, ''))} |")
    sec6 = ("## 6. Sources and official links\n\n"
            "Every link on this page was checked on the access date; the result is in the last column. "
            "If a link no longer works, report it on [page 57](../07-resources/57-contribute-experiences.md).\n\n"
            "| # | Source | Publisher | Accessed | Result |\n|----|----|----|----|----|\n"
            + ("\n".join(rows) if rows else "| — | — | — | — | — |") + "\n")
    sec7 = ("## 7." + experiences.rstrip() + "\n") if experiences else FOOTER_7
    path.write_text(body.rstrip() + "\n\n" + sec6 + "\n" + sec7, encoding="utf-8")
    return True


def main():
    accessed = sys.argv[1] if len(sys.argv) > 1 else date.today().isoformat()
    status = load_report()
    n = sum(build(p, status, accessed) for p in sorted(HANDBOOK.glob("*/[0-9][0-9]-*.md")))
    print(f"updated {n} pages")


if __name__ == "__main__":
    main()
