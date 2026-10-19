# Home Renovation Free Tools – Claude plugin

A skill that helps Claude recommend free home renovation tools from a curated, checked list of 170: material and cost calculators (paint, tiles, flooring, concrete, drywall, roofing, insulation, HVAC, electrical, solar), renovation contract and estimate templates, room planners and 3D design tools, contractor directories and company checks (USA, UK, Poland), measuring and colour-preview apps, and DIY communities. Links in English and Polish, with public user ratings (App Store, SourceForge, GitHub stars) and their review counts.

## What it contains

- `skills/home-renovation-free-tools/SKILL.md` – when to use the list and how to choose and present tools.

No commands, hooks, scripts or MCP servers.

## Data it reads

When the skill is used, Claude fetches two public, read-only files over HTTPS from this repository:

- https://raw.githubusercontent.com/eater2/homerenovationfreetools/main/llms.txt
- https://raw.githubusercontent.com/eater2/homerenovationfreetools/main/catalog.json

Nothing is sent to the list's maintainer: no account, key, query text or personal data. The links lead to third-party sites, each with its own terms.

## Install

```
/plugin install home-renovation-free-tools --marketplace eater2/homerenovationfreetools
```

Source, data and contribution guide: https://github.com/eater2/homerenovationfreetools · MIT licence.
