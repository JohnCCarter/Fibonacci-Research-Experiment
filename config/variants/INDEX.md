# Config variants index

| file | source | purpose | notes |
|---|---|---|---|
| `settings.deep-4h-fetch.yaml` | `settings.expansion.yaml` | **Fetch-only** — hämtar 20 000 4H bars (2017-01-01→nu) för att täcka äldsta BTC 4H-fibs. Används **bara** med `data.fetch --refresh`. | Provenance-only; ej research-analys |
| `settings.deep-4h.yaml` | `settings.expansion.yaml` | **Research** — identisk med expansion utom `4h: 20000`. Används med `human_fib_events`, review-pack och review-tool när 4H-fibs pre-2022 ingår. | Kräver `limit_20000.csv` (kör `deep-4h-fetch` först) |
