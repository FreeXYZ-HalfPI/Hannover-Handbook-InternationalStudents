# Changelog

To stay informed: check this page, click **Watch** on GitHub (or Watch → Custom → Releases) to get e-mail notifications, or follow the [ISL Telegram channel](https://t.me/hannover_iranian_students). Every single change: [commit history](https://github.com/FreeXYZ-HalfPI/Hannover-Handbook-InternationalStudents/commits/main).

> [!CAUTION]
> This handbook is guidance based on students' experience and may be out of date. ISL accepts no responsibility for its currency.

## 2026-11-10 — Goals and link re-check

- **New [ROADMAP.md](ROADMAP.md):** main goal, principles, today's figures and seven goals with open tasks; linked from the README and CONTRIBUTING.
- **New page 0 — First 14 days checklist:** the order of the first two weeks with a link to each task's page; added to the Section 1 contents and the README.
- **⚠️ tracking:** 33 issues (#2 to #34) cover the 56 open ⚠️ items, labelled `needs-verification` and `needs-owner`.
- **All external links re-checked** (342 checked, 321 answered 200; access dates are now 2026-11-10). The remaining failures are blocked or unreachable sites: `esn.org`, `github.com/signup`, 116117 appointments, Goethe-Institut, TestDaF (HTTP 500) and LinkedIn; 15 `gesetze-im-internet.de` addresses did not answer from the check machine but open in a browser.
- **AStA refund row (30):** one link still pointed to the 404 "translate-to-english-semesterticket" address; it now points to the current Semester ticket page.

## 2026-11-08 — Link re-check and fixes

- **All external links re-checked** (333 that answered 200 now carry the access date 2026-11-08).
- **AStA semester-ticket page (30):** the English address returned 404; it now points to the current "Semester ticket" and "Refunds & Exemptions" pages.
- **Minijob source (40):** the iww.de article returned HTTP 500 on the check date and is marked as failing; the official Deutsche Rentenversicherung source on the same page gives the same figure.
- **README PDF link:** the link text and URL were split over two lines and did not render on GitHub; fixed.
- **CONTRIBUTING:** the issue link is now the full GitHub address.
- **Still open:** TestDaF (HTTP 500), ESN section finder and Goethe-Institut (bot protection), LinkedIn (needs a login), `github.com/signup` (bot protection).

## 2026-11-03 — Link re-check and status update

- **All external links re-checked** (331 unique addresses). Pages with confirmed links now carry the access date 2026-11-03.
- **Replaced a dead link:** the Federal Ministry of the Interior naturalisation page (page 46) returned "page not found" after the BMI site redesign. It now points to the BAMF page [Naturalisation in Germany](https://www.bamf.de/EN/Themen/Integration/ZugewanderteTeilnehmende/Einbuergerung/einbuergerung.html).
- **Status changed from "blocks automated checks" to opened** after manual browser checks: Goethe-Institut practice page (page 35), 116117 appointment service (page 29), MHH psychotherapy counselling (page 29), KZVN dentist search (page 33).
- **Still open:** TestDaF returned HTTP 503 on the check date; ESN section finder shows a Cloudflare challenge in automated browsers; LinkedIn requires a login.
- **Website and automation:** the handbook is published at [freexyz-halfpi.github.io/Hannover-Handbook-InternationalStudents](https://freexyz-halfpi.github.io/Hannover-Handbook-InternationalStudents/) with a strict build check, a weekly link check, and a release-PDF job, all as in the ISL repository.
- **`tools/refresh.py`:** one command re-checks the links, updates access and review dates, refreshes the page boxes and, with `--build`, rebuilds the search index and PDF.
- **Refugee information (page 63)** now links to the canonical Study in Germany page.


## 2026-10-29

- **Feedback buttons on every page:** the box at the top of each page now has one-click links to report an error, suggest an idea, share an experience or edit the page; each opens a GitHub issue with the page's path in the title. New "Idea or feedback" issue template, and a "tell us" link at the bottom of the Handbook Searcher.

## v1.0.0 — 2026-10-27 — first release

- **Copyleft:** all text, diagrams, the PDF and code under the GNU GPL v3 or later; "Copyright" replaced by "Copyleft 🄯".
- Repository description and topics on GitHub.
- **Large disclaimer** at the top of every page, with the page's last update date.
- **Medical disclaimer** on pages 7 (health insurance), 29 (counselling), 33 (doctors and pharmacies) and 37 (emergency).
- This changelog.

Download the PDF of this version: [Releases](https://github.com/FreeXYZ-HalfPI/Hannover-Handbook-InternationalStudents/releases/latest)

## 2026-10-26

- Ported the ISL handbook's October updates (19 pages) and added pages 65 (annual calendar), 66 (passport, documents, translations and certified copies), 67 (consumer rights and free legal help) and 68 (GitHub guide).
- **Handbook Searcher** (`search/index.html`, `tools/search.py`): searches this handbook and the Persian ISL handbook together.

## 2026-10-25

- Re-checked all links; fixed the dead Bundesnetzagentur link.

## 2026-10-24

- First version: 64 pages for international students of every nationality, PDF and tools.
