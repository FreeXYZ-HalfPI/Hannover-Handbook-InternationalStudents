# Hannover Handbook — International Students

**Living in Hannover — A Practical Handbook for International Students at Leibniz University Hannover**

A practical, step-by-step handbook in English for **international students from every country** at Leibniz University Hannover (LUH): from applying while still at home, to arriving in Hannover, studying, working, and staying after graduation. Open to everyone's contributions.

📖 **Start reading:** [handbook/README.md](handbook/README.md) · 🌍 **Rules for your nationality:** [Section 8](handbook/08-by-nationality/README.md) · 📄 **PDF:** [pdf/Hannover-Handbook-International-Students.pdf](pdf/Hannover-Handbook-International-Students.pdf) · 🔎 **Search both handbooks:** [search/index.html](search/index.html) (download the repository and open it in your browser) or `python3 tools/search.py your words`

---

## What is this handbook?

Each topic has one page, and every page follows the same structure: purpose, who needs it, steps, documents and costs (required or possible), responsible office, official sources with **access date** and the result of a link check, and student experiences.

| Section | Pages |
|---|---|
| [1 — Arriving in Hannover & First Steps](handbook/01-arriving-in-hannover/README.md) | 1–11 |
| [2 — Starting Your Studies at LUH](handbook/02-starting-your-studies/README.md) | 12–20 |
| [3 — University Services & Student Support](handbook/03-university-services/README.md) | 21–29 |
| [4 — Everyday Life in Hannover](handbook/04-everyday-life/README.md) | 30–39 |
| [5 — Work, Finance & Career](handbook/05-work-finance-career/README.md) | 40–47 |
| [6 — Student Community & Engagement](handbook/06-student-community/README.md) | 48–52 |
| [7 — Resources & Appendices](handbook/07-resources/README.md) | 53–57 |
| [8 — Information by Nationality and Specific Needs](handbook/08-by-nationality/README.md) 🌍 | 58–64 |

**Section 8** covers what differs by citizenship or status: EU/EEA and Swiss citizens, visa-free nationalities (Australia, Canada, Israel, Japan, New Zealand, South Korea, UK, USA, …), visa-required countries and the APS certificate (China, India, Vietnam), sanctions and banking restrictions, refugees and people with temporary protection (e.g. Ukraine), and religion, food and home communities.

## Contributing

Everyone can help: correct a figure or deadline, report a broken link, add a personal experience (especially country-specific tips) or write a new page. See [CONTRIBUTING.md](CONTRIBUTING.md). The core rule: **every claim needs an official source, and every source needs an access date.**

> [!WARNING]
> This handbook is general guidance, not legal, tax or medical advice. The responsible official office always has the final word.

---

## Repository layout

| Path | Content |
|---|---|
| `handbook/` | The handbook: one Markdown file per topic, one folder per section |
| `pdf/` | The printable PDF, built from `handbook/` |
| `tools/check_links.sh` | Checks every external link in `handbook/` and writes `link-report.tsv` |
| `tools/build_sources.py` | Regenerates each page's sources table (section 6) from its links and `link-report.tsv` |
| `tools/build_pdf.py` | Builds the PDF (needs pandoc ≥ 3.1 and Chrome/Chromium) |
| `search/index.html` | **Handbook Searcher** — searches both handbooks (English and Persian) in your browser, offline; open the file or serve the folder |
| `tools/build_search.py` | Rebuilds `search/search-index.js` from both handbooks (the sibling repository is included when it is checked out next to this one) |
| `tools/search.py` | The same search in the terminal: `python3 tools/search.py residence permit` |
| `handbook/images/` | Diagrams used in the handbook (SVG) |
| `TEMPLATE.md` | Template for new pages |

```bash
bash tools/check_links.sh
python3 tools/build_sources.py
python3 tools/build_search.py
python3 tools/build_pdf.py
```

## Origin

This handbook is an English, nationality-neutral adaptation of the Persian-language [Hannover Handbook — ISL](https://github.com/FreeXYZ-HalfPI/Hannover-Handbook-ISL) by the Iranian Students Association of Leibniz University Hannover (ISL). Content specific to Iran and Iranian students was removed, all other pages were translated and updated, and a new section on nationality-specific needs was added.

## License

Copyright © 2026 Iranian Students Association of Leibniz University Hannover (ISL) and contributors.

This handbook is free: you can redistribute it and/or modify it under the terms of the **GNU General Public License, version 3** or (at your option) any later version — see [LICENSE](LICENSE). Every copy or adaptation must stay under the same license (copyleft). Facts and links come from the official sources cited on each page; those sources keep their own terms.
