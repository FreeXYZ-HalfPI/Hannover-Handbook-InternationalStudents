# Goals & Roadmap

This page says what the handbook is for, what we want it to reach and where we are now. Every goal has a number you can count, so anyone can see whether we are really making progress. **Status as of 2026-11-10.**

## 1. Main goal

**Reduce the problems of new international students in Hannover:** fewer missed deadlines, less searching through scattered information, and every administrative step done in the right order with an official source.

## 2. Principles

1. **Every claim has an official source, and every source has an access date.** If there is no official source, the line is marked ⚠️ or "unofficial source" and is never hidden.
2. **Guidance, not legal advice.** The responsible authority always has the last word.
3. **Anyone can correct it.** The repository is free and copyleft; contribute through an issue or a pull request.
4. **Quality is measurable.** Links are checked automatically and ⚠️ items are tracked.

## 3. Status today

| Measure | Status |
|---|---|
| Content pages | 68 |
| Content size | about 67,000 words |
| External links checked | 342; 321 answered 200 |
| Links with a problem | 6 blocked or failing: `esn.org`, `github.com/signup`, 116117 appointments, Goethe-Institut, TestDaF (HTTP 500), LinkedIn |
| Links that only look broken | 15 `gesetze-im-internet.de` addresses did not answer from the check machine but open in a browser |
| Open ⚠️ items | about 59 on 36 pages, not yet tracked in issues |
| Automatic link check | every Monday with GitHub Actions; result in issue #1 |
| Website | live; rebuilt on every change |

## 4. Goals and plan

### Goal 1 — a clear path for the first weeks
- ⬜ A "first 14 days" checklist page that links every task to its page (the Persian handbook already has one).

### Goal 2 — no open ⚠️ items
- **Measure:** number of open ⚠️ items; today about 59, target 0 (or each with a clear reason "no official source").
- **Method:** one issue per page with the label `needs-verification`; a volunteer takes it, adds the official source and removes the ⚠️.
- ⬜ Create these issues (the Persian handbook has done this: issues #8 to #28).
- ⬜ Assign an owner for each issue.

### Goal 3 — healthy links
- **Measure:** failing links other than bot blocking; today 6, all known.
- ✅ Weekly automatic check and `python3 tools/refresh.py`.
- ⬜ Find alternative official sources for the blocked pages where one exists.

### Goal 4 — coverage of missing topics
Questions students ask often that do not yet have their own page. Suggestions to check against what is already covered:
- ⬜ Housing benefit (Wohngeld)
- ⬜ Household contents and liability insurance
- ⬜ Erasmus and exchange
- ⬜ Doctoral studies
- ⬜ Childcare and pregnancy
- ⬜ Unemployment and job search after graduation
- ⬜ Bicycles (buying, locks, theft)
- ⬜ Library and university resources

Start any of them with the "Suggest a new topic" issue template.

### Goal 5 — country-specific information (Section 8)
- ⬜ More tested tips per nationality or status: visa waiting times, document legalisation, home-country scholarships, banking.
- ⬜ Reviewers who recently went through the same process.

### Goal 6 — trust and review
- ⬜ A reviewer for each legal or administrative page.
- ⬜ A language review of the English text.
- ⬜ Release v1.1.0 with the PDF.

### Goal 7 — both languages in step
- ⬜ Keep this handbook in step with the Persian one (headings and links).
- ⬜ An automatic check for differences between the two repositories.

## 5. How can I help?

- Take a ⚠️ item once the issues exist, or fix one directly with a pull request.
- Suggest a topic: [new issue](https://github.com/FreeXYZ-HalfPI/Hannover-Handbook-InternationalStudents/issues/new/choose)
- Writing rules: [CONTRIBUTING.md](CONTRIBUTING.md)

## 6. Keeping this page current

Update the status table (section 3) after every link check (`python3 tools/refresh.py`) and whenever the ⚠️ items change. Changes are recorded in the [changelog](CHANGELOG.md).
