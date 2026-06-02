# premortem/reflections

Löpande reflektioner från körningar och beslut. Obligatoriskt enligt `repository-layout-policy.md` §11.

**Översikt:** [INDEX.md](INDEX.md) — uppdatera när du lägger till en ny fil.

---

## Filnamn (MÅSTE)

```
YYYY-MM-DD-<kort-beskrivning>.md
```

- **Datum** = när reflektionen skrivs (inte nödvändigtvis körningens dag).
- **Beskrivning** = 2–5 ord, `kebab-case`, inga mellanslag.
- En fil per **beslut eller tydlig lärdom** — inte dagbok.

---

## Innehåll (MÅSTE)

```md
# YYYY-MM-DD <Titel>

Hypotes:
- ...

Scope:
- Exchange / symboler / timeframes / data:

Observationer:
- ...

Beslut:
- ...

Nästa steg:
- ...
```

Valfritt YAML-frontmatter överst (rekommenderat när mappen växer):

```yaml
---
type: run | decision | learning | premortem
topics: [labeling, validate, backtest]
related: [docs/MACHINE_LABELING.md]
supersedes: 2026-05-28-earlier-decision   # om denna ersätter äldre slutsats
status: active | historical
---
```

---

## När ska en ny reflektion skrivas?

| Händelse | Exempel |
|----------|---------|
| Validate-körning med beslut | Ny matris, pivot_recall-runda |
| Policy/arbetsätt ändras | Ändra researchflöde, inför maskin-labeling |
| Facit eller promotion | Godkänd BTC 1w, merge till `settings.yaml` |
| Överraskning / missförstånd | Chartfönster vs motor-swing → `docs/MACHINE_LABELING.md` |

**Skippa** triviala commits (typo, ren format) utan beteendeförändring.

---

## Storlek (MÅSTE — håll reflektioner korta)

Reflektioner är **anteckningar**, inte rapporter. Gräns (kontrolleras av `repo-bounds` i pre-commit, se `repository-layout-policy.md` §2B):

| Gräns | Värde |
|-------|--------|
| Rader | **≤ 80** (exkl. `INDEX.md`, `README.md`) |
| Filstorlek | **≤ 8 KiB** |

**Gör så här:**

- **Observationer:** 3–7 punkter, nyckeltal (t.ex. `flip_rate`, `gate_passed`) — inte hela tabeller.
- **Data:** peka på `experiments/results/<ledger>.jsonl` + `run_id` / `config_hash`.
- **Lång förklaring:** ny eller utökad fil under `docs/` (t.ex. `docs/MACHINE_LABELING.md`), en rad i reflektionen som länkar dit.
- **Rå JSON/CSV:** lägg i `experiments/`, aldrig klistra in i reflektionen.

**Om gränsen inte räcker:** dela upp — en reflektion = ett beslut; skapa `docs/…` för bakgrund.

---

## Skalning — när mappen blir stor

### Nu (≤ ~30 filer i rot)

- Alla `.md` direkt under `reflections/`.
- **[INDEX.md](INDEX.md)** hålls manuellt uppdaterad (en rad per fil).

### Nästa steg (~30+ filer eller nytt kalenderår)

1. Skapa **`reflections/YYYY/`** (t.ex. `2026/`).
2. **Nya** reflektioner läggs i årets mapp: `reflections/2026/2026-05-29-foo.md`.
3. Lägg **inte** om gamla filer i onödan — länkar i docs/git-historik ska fungera.
4. Uppdatera INDEX med sektion per år.

### Lång sikt (100+ filer)

- Överväg **ämnesundermappar** endast om INDEX blir ohanterlig:
  `reflections/2026/labeling/`, `validate/`, `infra/`.
- **Arkivera** superseded reflektioner: flytta till `archive/premortem/reflections/` och markera
  `status: historical` i INDEX (flytta inte utan att uppdatera INDEX + ev. pekare i docs).

### Vad vi inte gör

- Ingen en fil per dag “för rutin”.
- Ingen duplicering av hela experiment-loggar — peka på `experiments/results/*.jsonl` + `run_id`.
- Ingen auto-tuning-mot-facit som egen reflektionskategori utan beslut mot princip.

---

## Koppling till övriga docs

| Behov | Var |
|-------|-----|
| Övergripande risker | [../PREMORTEM.md](../PREMORTEM.md) |
| Backtest-faser | [docs/FIB_BACKTEST_PLAN.md](../../docs/FIB_BACKTEST_PLAN.md) |
| Maskin-labeling A/B | [docs/MACHINE_LABELING.md](../../docs/MACHINE_LABELING.md) |
| Repo-regler | [repository-layout-policy.md](../../repository-layout-policy.md) §11 |
