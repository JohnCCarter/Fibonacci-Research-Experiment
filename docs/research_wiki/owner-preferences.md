# Owner Preferences — vem ägaren är och hur han vill jobbas med

> Kanonisk, **git-synkad** sanning om ägaren. Endast git reser mellan hans maskiner (jobb · hemma ·
> iPhone), så denna sida — inte maskin-lokalt minne — är källan. Uppdateras av
> [`/owner-interview`](../../.claude/commands/owner-interview.md). Arbetsstil väger mot
> [north-star.md](north-star.md) och får **aldrig** överrida [AGENTS.md](../../AGENTS.md) eller
> forsknings-validitet.
>
> **Last verified:** 2026-06-30 · **Evidence:** owner interview 2026-06-30.

## Vem ägaren är

- **Trader/analytiker, nybörjarkodare, visions-drivare.** Domänen (marknad, chart, fib-urval) är hans
  hemmaplan; syntax är det inte.
- **Teknisk dragning:** arkitektur/AI + den GUI han faktiskt använder. **Backend: håll-det-borta**
  (~99 % delegeras till agenter) → bygg verktyg *för* agenter, inte krav på att han dyker i motorn.
- **Lär-mig-längs-vägen:** vill förstå hur agenterna/systemet hänger ihop *medan* vi kör autonomt.
- **Rytm:** långa fokuspass, flera maskiner + mobil → git är enda synk-kanalen.
- **Framgång om ett år (skärpt):** en **live Trader-agent**.

## Den verkliga "frontend"-ytan

Det är **inte** en generell webb-frontend. Hans primära UI är **labeling-toolen**
([`labeling/tool.py`](../../src/fibengine/labeling/tool.py), Matplotlib-GUI) där han ritar sina fibs.
UI-omtanke hör hemma *där*: tydlighet och flöde i själva fib-ritningen, inte i en separat app.

## Hur man jobbar med honom (guardrails)

- **Slutsats-först, kort summering** ([AGENT_RESPONSE_STYLE](../agent/AGENT_RESPONSE_STYLE.md)).
  Drunkna honom inte i text.
- **Autonomt;** check in **bara när det spelar roll**.
- **Vid gaffel/vägval:** rekommendation först, **ingen sockring**; använd `AskUserQuestion` (knappar),
  inte prosa.
- **Inga genvägar.** Default = den riktiga lösningen. Välj den enkla vägen *bara* om den ger
  **betydligt** mer värde än den svåra.
- **Friktion att aktivt motverka** (alla fyra kryssade 2026-06-30): blir flaskhalsen · för mycket text
  · saker går sönder · oklart vad som ändrades → kör autonomt **men** lämna ett kort, läsbart spår av
  *vad* som ändrades och *att* gates är gröna.

## Ändringar fångade 2026-06-30 (diff mot tidigare körning)

- Teknisk dragning breddad: **+ Arkitektur/AI** bredvid GUI.
- Framgång skärpt: från "verktyg + agent" → **enbart live Trader-agent**.
- "Frontend" omdefinierad: = **labeling-toolen**, inte en separat app.
- **Lär-mig-längs-vägen** tillagt.
- Friktion: **alla fyra** kryssade (stark signal — väg tungt).
