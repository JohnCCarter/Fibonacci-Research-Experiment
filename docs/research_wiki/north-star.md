# North Star — vad projektet är (och inte är)

> Kanonisk avsiktsförklaring. Allt arbete vägs mot den här sidan. När en linje inte tjänar den
> här frågan: parkera den. (Formulerad av användaren 2026-06-25; detaljerad status i
> [handoff.md](handoff.md), historik i [log.md](log.md).)

## Idén (en mening)

**Lär maskinen att se chartet som människan gör** — så att den, av sig själv, väljer Fib precis
som användaren skulle:

> **Chart → hitta meaningful high/low → välj rätt leg/range → rita Fib som Chamoun hade gjort.**

Maskinen ska lära sig *varför just de* swing-highs/lows hör ihop som ett fib-ben/range. **Facit =
användarens manuella source-fibs** (human fib = sanningen modellen lär sig från; `*_candidate` ≠
facit; ingen auto-fib som sanning).

## Slutmålet — ja, detta ska bli en edge

Destinationen är uttrycklig: det här ska **till slut** bli en edge / trading-signal, **backtestas**,
och **integreras i Genesis-V2**. Det mänskliga urvalet är *fundamentet* — inte hela målet.

## Sekvensen (det guardrails egentligen vaktar: ordning, inte tak)

1. **Steg 1 — mänskligt urval (hela jobbet just nu, ej i mål):** motorn väljer/ritar Fib som
   människan. "Gör den det så hamnar allt på plats."
2. **Steg 2 — deskriptiv nivå-avläsning:** när candles når nivåerna klassificeras varje touch.
   Taxonomin finns redan i [`level_events.py`](../../src/fibengine/research/level_events.py) som fyra
   **post-hoc** `*_candidate`-typer (efterhandsannotation via ett `forward_window`, *aldrig* en
   live-signal):
   - **continuation** — bröt igenom nivån och fortsatte.
   - **rejection** — touch och reject tillbaka till approach-sidan.
   - **failure** — accepterade bortom nivån, vände sedan tillbaka över den (falsk break).
   - **reaction** — reagerade vid nivån utan tydlig break/reject.

   Plus: vilka nivåer som får mest interaktion. Först meningsfullt när steg 1:s nivåer faktiskt är
   människans nivåer (kvaliteten ärvs uppåt från steg 1).
3. **Steg 3 — edge-hypotes + backtest:** testa OOS, utan leakage, mot matchade kontroller.
4. **Steg 4 — integration i Genesis-V2.**

> Repots stående *no edge / behaviour / PnL / backtest / Genesis / auto-fib-as-truth claim* betyder
> **inte "aldrig"** — det betyder **"inte ännu / inte från den här delstudien"**. Det är en
> validitets-grind som *skyddar* den framtida edgen: claimar man edge före steg 1 funkar och före
> riktig OOS-test, ärver Genesis-V2 en falsk signal. **Disciplinen tjänar destinationen.**

## Ärlig status (2026-06-25) — steg 1 är inte i mål

- **Selection-learning-linjen ÄR steg 1** (få motorn att välja som människan) — den var *inte*
  driften. Driften var ett sidospår *inuti* linjen: detektor-mekanik (snapping, net-vs-path,
  artefakt-prober). [Main-quest reset](reviews/btc-fib-selection-learning-main-quest-reset-20260624.md)
  drog tillbaka till urvalsfrågan.
- **Vad motorn klarar:** rangordnar människans legs **långt över slumpen** (AUC ≈ 0.91; AP ≈ 11×
  baseline), stabilt över confirmation-buffer `k ∈ {3,6,12}`
  ([`k_stable_live_selection_signal`](reviews/btc-fib-selection-learning-results-20260618.md)).
- **Vad den inte klarar:** den **reproducerar inte** urvalet — absolut AP 0.057 mot tak 0.83, och
  ledningen vilar nästan helt på *ett* mått: `cleanliness` (netto-rörelse ÷ total väg = hur ren/rak
  legen är). Den ser att dina legs är *renare*, men ser dem inte som *dig*.
- **Enrichment-skottet** (`exclusivity`/leg-completeness) gjorde det sämre →
  [per-leg-feature-linjen stängd](reviews/btc-fib-selection-learning-enrichment-results-20260625.md).
- **Öppen crux:** är `cleanliness`-ledningen äkta omdöme eller en detektor-artefakt? Den inflations-
  artefakten är *försvagad* men inte avfärdad; det avgörande matched-null-testet är ogjort.

## Nästa brygga mot visionen

Gapet "rangordnar över slump" → "väljer som dig" stängs troligast av **mer/bättre facit**
(mänskliga labels), inte av fler features. Se fork i [handoff.md](handoff.md) §Next Step.
