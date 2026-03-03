# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a static documentation repository — a curated "awesome list" of free tools, calculators, and resources for home renovation projects. There is no application code, build system, or dependencies. The entire project content lives in `README.md`.

## README Format

The README uses **raw HTML** (not Markdown syntax) for all structural elements:
- Sections use `<h2>` and `<h3>` tags with emoji prefixes
- Tool listings use `<table>` elements with `<thead>`/`<tbody>` structure
- Each table row has two columns: tool name and a link ("Go to Tool" or "Visit")
- Community links use `<ul>`/`<li>` elements
- Sections are separated by `<hr>` tags

## Sections

1. **Featured Renovation Calculators** — material/cost estimator links
2. **Documents Generators** — lease, handover, and contract generators
3. **Design & Visualization Tools** — room planners and 3D modeling tools
4. **Useful Mobile Apps** — renovation and design apps
5. **Community & Learning Resources** — Reddit communities and DIY sites
6. **Contributing** / **License**

## Known Issues

- There is a nested `<table>` tag issue at lines 8–12: an outer `<table>` wraps the calculators section header, with a second `<table>` inside for the actual data, but only one closing pair at lines 91–92. This renders correctly on GitHub but is structurally invalid HTML.
- The LICENSE file referenced at the bottom does not exist in the repository.
