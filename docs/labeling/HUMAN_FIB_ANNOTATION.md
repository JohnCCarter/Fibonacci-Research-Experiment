# Human fib-annotering (`fibengine.labeling.human_fib`)

**Manuell ground truth.** Människan ritar fiben; den ritade fiben **är facit**.
Maskinen får här bara: *läsa, lagra, räkna nivåer, och klassa candle-interaktion*
mot de sparade nivåerna.

**Ingen auto-fib.** Modulen har ingen detektor och gissar aldrig en range — ankare
kommer alltid från en människa. Ingen tuning, inga edge-påståenden, research-only
(läses inte av motorn/eval/promotion).

### Varför human-fib på 1d? (MTF-ursprung)

Projektet startade på **1w**: H→L, fib-grid, några nivåträffar på veckobars. När **samma H/L-range** lades på **1d** syntes **fler** candle-interaktioner vid samma fib-nivåer — daily visar **HUR**, weekly visar **VAD**.

Det ska stå som grund i [MTF_DAILY_RESEARCH.md](MTF_DAILY_RESEARCH.md) **§0 (läs först)**. Human-fib-filerna (`w`) är research-sättet att spara många sådana 1d-upplösta legs/gridar, inte ersättning för `1w.json`-facit.

---

## Skapa en annotering

### I labeling-verktyget (GUI)

Sätt **high** + **low** som vanligt, tryck sedan **`w`**. Annoteringen sparas till:

```text
data/labels/human_fib/{exchange}/{symbol}/{timeframe}/{fib_id}.json
```

Detta är skilt från `s` (som sparar swing-`legs[]` i det vanliga facit-formatet).
`anchor_a` = det tidigaste picket, `anchor_b` = det senaste; `direction` härleds
ur priserna.

### Utan GUI (CLI)

```bash
uv run python -m fibengine.labeling.human_fib \
  --symbol BTC/USD --timeframe 1d \
  --anchor-a-time 2026-01-14T00:00:00Z --anchor-a-price 97924 \
  --anchor-b-time 2026-02-06T00:00:00Z --anchor-b-price 60000 \
  --classify
```

`--classify` läser cachade candles (`fetch_if_missing=False`) och skriver
`{fib_id}_interactions.csv` bredvid JSON-filen. Visa en sparad fil med `--show PATH`.

---

## Ankar-konvention (observerad review-praxis, 2026-06-15)

Inte en absolut global regel — en **observerad current review-konvention** från BTC/USD
4H-granskningen (Tier 2). Dokumenterad så att wick/body-frågor hanteras konsekvent:

- Vissa 4H crash-/impuls-ben ankras vid en **body/close-liknande nivå** snarare än den
  exakta **wick-extremen**. Exempel: Jan 2021-paret (`20210110T080000` /
  `20210110T200000`) delar `anchor_b` vid body/close (~30 635) i stället för wick-lowen.
- Detta ska **inte** automatiskt klassas som fel — wick-vs-body är en bedömningsfråga.
- En wick/body-avvikelse kan bli **watchlist** eller **correction-candidate** i
  review-ledgern, **inte** auto-fail.
- Ankaret bedöms mot det **strukturella benet och den lokala swingen**, inte enbart mot
  den extrema wicken.

Spårning: verdicts i [review-ledgern](../research_wiki/reviews/ledgers/README.md);
near-duplicate/overlap-kandidater via `research/overlap_detector.py`
([rapport](../research_wiki/reviews/btc-4h-overlap-candidates-20260615.md)).

## Datamodell

```json
{
  "fib_id": "fib_BTC-USD_1d_20260114000000",
  "symbol": "BTC/USD",
  "timeframe": "1d",
  "exchange": "bitfinex",
  "created_by": "human",
  "source": "manual_labeling_tool",
  "scale_mode": "log",
  "levels_profile": "tradingview_log_chamoun",
  "human_highlights": [],
  "anchor_a": { "time": "2026-01-14T00:00:00Z", "price": 97924.0 },
  "anchor_b": { "time": "2026-02-06T00:00:00Z", "price": 60000.0 },
  "direction": "down",
  "levels": [
    { "ratio": 0.0,   "price": 60000.0 },
    { "ratio": 0.382, "price": 72346.43 },
    { "ratio": 0.5,   "price": 76651.42 },
    { "ratio": 0.618, "price": 81212.57 },
    { "ratio": 0.786, "price": 88178.61 },
    { "ratio": 1.0,   "price": 97924.0 }
  ]
}
```

- **`anchor_b` är ratio 0.0, `anchor_a` är ratio 1.0.**
- **`scale_mode`:** `log` (aktiv BTC-profil) → `price(r) = b^(1−r) · a^r`
  (geometrisk interpolation, matchar TradingView "Fib levels based on log scale").
  `linear` → `price(r) = b + r·(a − b)`. Saknas fältet i en gammal fil → läses som
  `linear` (bakåtkompatibel).
- **`levels_profile`:** `tradingview_log_chamoun` = `[0, 0.382, 0.5, 0.618, 0.786, 1]`
  (**inget 0.236**). Alla nivåer är likvärdiga; ingen golden-zone-bias i sampling
  (Addendum 2 — `primary_active_levels` borttaget).
- **`human_highlights`:** valfria presentations-/review-annoteringar (t.ex. en zon
  0.5–0.618). Påverkar **bara** visning/filtrering, aldrig event-detektion, outcome,
  sampling eller nivå-vikt. Saknas → `[]` (bakåtkompatibel).
- **`direction`:** `down` om `anchor_a.price ≥ anchor_b.price`, annars `up`.
  Kan överskridas explicit (`--direction`).

---

## Candle-interaktion (deterministisk geometri)

För varje candle i scope klassas relationen till **varje** fib-nivå. Reglerna är
ömsesidigt uteslutande (prioritet uppifrån):

| Relation | Regel |
|----------|-------|
| `below`  | `high < level` (hela candlen under nivån) |
| `above`  | `low > level` (hela candlen över nivån) |
| `cross`  | nivån inom `[low, high]` **och** `open`/`close` på strikt motsatta sidor |
| `touch`  | nivån inom `[low, high]` men ingen strikt cross |

`classify_candles(df, annotation)` ger en rad per `candle × nivå`:
`time, ratio, level_price, relation, open, high, low, close`.

> **Inte** beteende-facit. `rejection` / `continuation` / `reaction` / `failure`
> sätts **inte** här — de kräver senare beteende-definitioner
> (se [BEHAVIOR_FACIT.md](BEHAVIOR_FACIT.md)). Lägg bara till sådana som *explicita
> manuella* labels när definitionerna finns.

---

## API (kort)

| Funktion | Vad |
|----------|-----|
| `make_annotation(...)` | Bygg annotering från explicita ankare (keyword-only) |
| `compute_levels(a, b)` | Härled nivåpriser |
| `infer_direction(a, b)` | `up` / `down` från priser |
| `classify_candle(o,h,l,c,level)` | En candle vs en nivå |
| `classify_candles(df, ann)` | Alla candles × alla nivåer |
| `save_annotation` / `load_annotation` | JSON-persistens |
| `anchors_from_picks(df, ...)` | Mappa GUI high/low-pick → `(anchor_a, anchor_b)` |

Tester: `tests/labeling/test_human_fib.py` (nivå-beräkning, above/below/touch/cross,
reload, ingen auto-fib).

---

## Behavior-candidates (nästa lager)

`fibengine.labeling.human_fib_events` matar din människoritade fib (facit-ankarna)
in i den befintliga `detect_level_events` och emitterar `*_candidate`-events per
nivå — *vägen* priset tar **efter** en touch, över ett framåt-fönster. Inga nya
formler, ingen auto-fib. **Candidates är aldrig facit** (se
[LEVEL_EVENTS.md](LEVEL_EVENTS.md)).

| Atom (per candle, `human_fib`) | Candidate (väg, detta lager) |
|--------------------------------|------------------------------|
| `touch` på nivån, retur till approach-sidan | `rejection_candidate` |
| `cross` + stannar på andra sidan (accept) | `continuation_candidate` |
| `cross` + accept bortom, sen `cross` tillbaka | `failure_candidate` |
| `touch`/`cross` utan tydlig breakout/rejektion | `reaction_candidate` |

Konventionen matchar exakt: `swing.start = anchor_a` (ratio 1.0),
`swing.end = anchor_b` (ratio 0.0) → `fib_levels(swing)` == dina nivåer, och
fönstret skannas efter `anchor_b` (legens slut).

```bash
uv run python -m fibengine.labeling.human_fib_events \
  --fib data/labels/human_fib/bitfinex/BTC-USD/1d/<fib_id>.json
```

Sparar `<fib_id>_events.json` bredvid annoteringen och skriver ut antal per
candidate och nivå. Tester: `tests/labeling/test_human_fib_events.py`.

---

## Relaterat

- [LABELING_TOOL.md](LABELING_TOOL.md) — GUI, tangenter, begränsningar
- [LEVEL_EVENTS.md](LEVEL_EVENTS.md) — `*_candidate`-taxonomi + guardrails (återanvänds av detta lager)
- [BEHAVIOR_FACIT.md](BEHAVIOR_FACIT.md) — beteende-facit (nästa lager, inte detta)
- [data/labels/README.md](../data/labels/README.md) — `source` human/machine
