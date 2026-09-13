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

- Put the tool in the section that fits it best, next to similar tools.
- The first rows of each section are the maintainer's own tools (airenovationcalculator.com / kalkulatorremontu.pl). **Add new entries below them.**

## Row format

Every table has four columns. Use `—` (em dash) when there is no version for a language, and write the last column in Polish:

```html
<tr>
  <td>Tool Name</td>
  <td><a href="https://example.com/tool">Go to Tool</a></td>
  <td>—</td>
  <td>Krótki opis narzędzia po polsku</td>
</tr>
```

Keep the HTML valid – one `<tr>` per tool, closed properly, inside the existing `<tbody>`.

---

## 🇵🇱 Po polsku (w skrócie)

Dodajemy tylko darmowe narzędzia związane z remontem, z bezpośrednim i działającym linkiem (bez parametrów afiliacyjnych) – jedno narzędzie na jeden PR. Nowe pozycje wstawiaj **poniżej** narzędzi z airenovationcalculator.com / kalkulatorremontu.pl, obok podobnych narzędzi. Brak wersji językowej oznaczaj `—`, a ostatnią kolumnę pisz po polsku.
