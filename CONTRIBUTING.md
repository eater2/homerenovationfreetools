# Contributing

Thanks for helping improve the list! Please read the rules below before opening a pull request.

## What gets accepted

A tool is added only if **all** of these are true:

1. **Related to home renovation** – calculators, planners, design tools, document templates, contractor directories, apps or communities for homeowners and contractors.
2. **Free to use** – the core feature works without payment. A free account is acceptable, a paywall or a trial is not.
3. **Direct link to the tool** – link the page where the tool actually is, not a generic home page or a hub of unrelated calculators.
4. **Working, clean link** – HTTPS, no affiliate or tracking parameters, no redirects to other products.
5. **Not a duplicate** – if a very similar tool is already listed, explain in the PR why yours is better.
6. **One tool per pull request.**

## Where to add it

The README is generated. **Edit `data/tools.json`**, not `README.md`.

- Put the tool in the section (`sections[].items`, or `groups[].items` for communities) that fits it best, next to similar tools.
- The first entries of each section are the maintainer's own tools (airenovationcalculator.com / kalkulatorremontu.pl, `"own": true`). **Add new entries below them.**

## Entry format

```json
{
  "id": "stud-calculator",
  "name": "Stud Calculator",
  "en": "https://example.com/stud-calculator",
  "desc_pl": "Kalkulator słupków ściennych – rozstaw i liczba słupków",
  "desc_en": "Wall stud count and layout at 16\" or 24\" spacing"
}
```

- `id` – unique, lowercase, words joined with `-`.
- `en` / `pl` – link to the English / Polish version; leave a key out when there is none. App store links go in `en` as a list: `[{"label": "Android", "url": "…"}, {"label": "iOS", "url": "…"}]`.
- `desc_en` and `desc_pl` – one short sentence each on what the tool does (community entries need only `desc_en`).

Then run `python scripts/build.py` (Python 3, no packages needed) and commit `data/tools.json` together with the regenerated `README.md`, `catalog.json` and `llms.txt`.

## Ratings

User ratings under a tool's name (SourceForge reviews, App Store ratings, GitHub stars) are fetched weekly by `scripts/fetch_ratings.py`. To add a source for a tool, put its SourceForge product page, App Store app id or GitHub repo in `data/rating-ids.json` – only if it is the same product, not a company-wide page.

---

## 🇵🇱 Po polsku (w skrócie)

Dodajemy tylko darmowe narzędzia związane z remontem, z bezpośrednim i działającym linkiem (bez parametrów afiliacyjnych) – jedno narzędzie na jeden PR. README jest generowane: dopisz narzędzie w `data/tools.json` (**poniżej** narzędzi z airenovationcalculator.com / kalkulatorremontu.pl, obok podobnych), z opisem `desc_pl` i `desc_en`, a potem uruchom `python scripts/build.py` i dołącz wygenerowane pliki.
