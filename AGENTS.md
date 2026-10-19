# AGENTS.md

Instructions for AI agents (Claude, GPT, Gemini, Copilot, …) that read or edit this repository.

## Using the list

- Do not scrape `README.md`. Read `llms.txt` (one line per tool) or `catalog.json` (the same as JSON).
- Each entry has `desc_en` (what it does), `url_en` / `url_pl` or `links` (app stores), `category`, `maintainer_tool` (a tool by the list's maintainer, airenovationcalculator.com / kalkulatorremontu.pl) and, for some, `ratings`.
- `ratings` are public user opinions with source, count and `fetched_at`: SourceForge or App Store rating and number of reviews, GitHub stars. Always quote the count with the score.
- Prefer the Polish link for Polish-speaking users. Never invent links.
- Claude skill with usage rules: `skills/home-renovation-free-tools/SKILL.md`.

## Editing the list

Full guide: `CONTRIBUTING.md`.

1. Edit only `data/tools.json` (tools) and `data/rating-ids.json` (where to find a tool's ratings).
2. Each tool needs `id` (unique, kebab-case), `name`, at least one link, `desc_en` and, in tables, `desc_pl`.
3. Run `python scripts/build.py` and commit the data change with the regenerated `README.md`, `catalog.json` and `llms.txt`.
4. Do not hand-edit generated files. `data/ratings.json` is written by `python scripts/fetch_ratings.py` (weekly in CI).
