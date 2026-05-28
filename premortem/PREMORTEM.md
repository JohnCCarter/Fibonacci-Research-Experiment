# Premortem — Fibonacci-engine

Tänk dig att projektet har misslyckats. Vad gick fel? Fyll på listan löpande.

## Hypotetiska misslyckanden

- **För få facit-exempel.** Heuristiken tunas mot en handfull chart och
  överanpassas. → Samla minst 20–30 labelade setups innan vikter låses.
- **Facit är inkonsekvent.** Samma setup labelas olika vid olika tillfällen.
  → Skriv ned en kort regel för hur du själv väljer swing, labela mot den.
- **Pivot-detektorn missar de swingar du faktiskt ritar på.** Om kandidaterna
  inte ens innehåller "rätt" punkt kan ingen viktning rädda det.
  → Mät *recall* på facit-pivoterna separat innan scoring optimeras.
- **ATR-normaliseringen döljer skillnader mellan instrument/timeframe.**
  → Utvärdera per symbol/timeframe, inte bara aggregerat.
- **Score-modellen blir en svart låda trots linjäritet.** Vikter driftar utan
  spårning. → leaderboard.jsonl + config-hash per run; ändra en sak i taget.
- **Look-ahead bias.** Features råkar använda framtida barer.
  → Håll all feature-beräkning kausal (bara data ≤ aktuell bar).
- **Att smyga tillbaka till att optimera mot exemplen.** Exemplen är referens,
  inte domare. Frestelsen att "tuna upp agreement-%" gör att modellen kopierar
  dina exakta linjer istället för principerna. → `agreement` är *en* sanity-
  signal bland flera; vikter sätts på principgrund, aldrig auto-tunas mot facit.
- **Lager A läcker in i Lager B (eller tvärtom).** Sizing/exekvering börjar
  påverka swing-urvalet. → Håll `sizing/` helt frikopplat; det läser urvalets
  output men matar aldrig tillbaka in i score eller metrics.
- **Godtyckliga confluence-grader / överanpassning av skal-parametrar.** Att
  trimma `confluence_degrees`/`confluence_tol_bars` tills en favoritsväng vinner
  är att överanpassa. → Håll graderna få och principmotiverade; ändra en sak i
  taget och spåra i leaderboard.
- **Att handla på en provisorisk Fib.** En provisorisk swing kan fortfarande
  flytta sin endpunkt (priset gör nya highs/lows) → Fib-nivåerna skiftar.
  → Agera bara på `status == "confirmed"`; behandla provisoriska som "håller på
  att formas".
- **Generalisering hävdas från en tunn matris.** 3 symboler × 3 timeframes säger
  lite om robusthet, och aggregatet döljer att enskilda rader är svaga (t.ex. BTC
  15m) eller har hög endpoint-drift trots bra flip-rate (t.ex. SOL 1h, ~52 barer).
  → rapportera alltid per symbol/timeframe, inte bara snitt; behandla
  matriskörningar som *Research*, inte Validate; kräv fler marknader/labels innan
  promotion.
- **Endpoint-drift ignoreras till förmån för flip_rate.** En "stabil" swing vars
  endpunkt ändå vandrar många barer är ekonomiskt instabil — låg flip_rate räcker
  inte. → gör `drift` till en förstklassig gate-metric vid sidan av
  flip/confirmed-rate.
- **Tyst label-exkludering döljer ett krympande sampel.** Out-of-window-labels
  exkluderas korrekt från recall/agreement, men om många faller bort beräknas
  måtten på allt färre punkter och ser bättre ut än verkligheten. → logga och spåra
  antalet exkluderade; åtgärda källan (label-tidsstämplar, längre fönster för
  1M/1w/1d), inte bara symptomet.
- **Confirm-trösklar för lösa eller för strikta.** `fractal_n=1` bekräftar redan
  efter en bar och `confirm_min_retrace=0.1` är lågt → swingar kan stämplas
  `confirmed` för tidigt. → övervaka att `confirmed_rate` håller sig i ett rimligt
  band; sätt trösklarna på principgrund och spåra ändringar i leaderboard, en sak i
  taget.
- **Coverage-gate ger falsk trygghet.** 60%-gaten + huvudsakligen happy-path-tester
  fångar inte adversariella fall (kausalitet testas men punktvis). → behåll
  kausal-/invariant-tester och utöka dem; höj aldrig promotion-status enbart på
  grön CI.
- **Spårmodellen kringgås.** Research-resultat (matriser, backtests) behandlas som
  Validate-evidens och promotas utan att gaten i `REPO_POLICY.md §13` är uppfylld.
  → ingen "trusted engine behavior" utan reproducerbar validate-körning + grön
  `pytest` + reflektion innan något når Promotion-ytan.

## Reflektioner per experiment

Lägg korta noter i `reflections/` (en fil per experiment): vad ändrades, vad
hypotesen var, vad utfallet blev, vad du lärde dig.
