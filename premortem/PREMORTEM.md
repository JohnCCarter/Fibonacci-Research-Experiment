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

## Reflektioner per experiment

Lägg korta noter i `reflections/` (en fil per experiment): vad ändrades, vad
hypotesen var, vad utfallet blev, vad du lärde dig.
