# VAD / HUR

VAD and HUR describe the top-down fib research split.

## Meaning

- **VAD**: what impulse or range is being measured. In the current protocol this
  is usually the higher-timeframe fib range, often weekly.
- **HUR**: how price behaves around that same range at a lower timeframe, often
  daily candles.

The observation that motivates the repo: a weekly H/L range can show only a few
level interactions on weekly candles, while the same range on daily candles shows
many more touches, crosses, and reactions.

## Practical Consequence

Do not treat a weekly label as a full daily behavior label. Weekly gives range
context; daily needs its own event review and sometimes its own labels.

The planned direction is top-down:

```text
1w VAD -> 1d HUR -> 4h finer structure -> 1h timing
```

## Source Links

- [MTF daily research](../../research/MTF_DAILY_RESEARCH.md)
- [HTF/LTF research alignment](../../research/HTF_LTF_RESEARCH_ALIGNMENT.md)
- [Research handoff](../../research/RESEARCH_HANDOFF.md)
