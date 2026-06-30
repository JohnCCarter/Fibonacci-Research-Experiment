#!/usr/bin/env bash
# UserPromptSubmit hook: ping when the context window crosses each sweet-spot threshold, so a
# checkpoint happens IN TIME — before thread-drift/compaction loses detail. The EARLY trigger;
# model-discretion invocation of /pre-compact-checkpoint proved unreliable (docs/research_wiki/log.md
# 2026-06-30).
#
# Thresholds = WINDOW_TOKENS * each PCT / 100. PCTS="35 40" of a 1M window (350k save-point, 400k
# MUST-compact). The fired ping is RELAYED to Chamoun by the agent (a hook can't post to his chat). Each
# threshold pings AT MOST ONCE per session; a jump past several at once pings only the highest (no
# double-nag). A /compact or /clear (detected as a big ctx drop vs the last turn) RE-ARMS the pings so
# they fire again in the same session. Tune PCTS / WINDOW_TOKENS below (lower on a smaller-window model). The
# context figure is READ from the transcript's latest usage (input + cache_read + cache_creation =
# tokens actually sent = current window occupancy) — the same number /context shows, not a turn guess.
#
# A hook can only REMIND, never invoke a skill. SONAR: pure bash + perl (Git Bash core, JSON::PP) —
# never python.exe / powershell.exe. exit 0 always (never blocks).

set -o pipefail
WINDOW_TOKENS=1000000
PCTS="35 40"               # Chamoun's thresholds: 350k save-point, 400k = MUST-compact (% of 1M); fire once each/session

input=$(cat)

# transcript_path + session_id from the payload (perl, no python). Read whole lines (paths have spaces).
meta=$(printf '%s' "$input" | perl -MJSON::PP -0777 -ne '
  my $d = eval { decode_json($_) } || {};
  print(($d->{transcript_path} // ""), "\n", ($d->{session_id} // "default"), "\n");
' 2>/dev/null)
transcript=$(printf '%s\n' "$meta" | sed -n '1p')
session=$(printf '%s\n' "$meta" | sed -n '2p')

[ -z "$transcript" ] && exit 0
[ ! -f "$transcript" ] && exit 0

# Current context occupancy = the last usage block in the transcript.
ctx=$(perl -MJSON::PP -ne '
  if (/"usage"/) {
    my $d = eval { decode_json($_) };
    my $u = (ref($d) eq "HASH") ? ($d->{message}{usage} // $d->{usage}) : undef;
    if (ref($u) eq "HASH") {
      $last = ($u->{input_tokens}//0) + ($u->{cache_read_input_tokens}//0)
            + ($u->{cache_creation_input_tokens}//0);
    }
  }
  END { print($last // 0); }
' "$transcript" 2>/dev/null)

[ -z "$ctx" ] && exit 0

state_dir="${TEMP:-${TMPDIR:-/tmp}}"
last_file="${state_dir}/fibengine-checkpoint-lastctx-${session}"

# Compaction reset: ctx only ever grows within a session, so a big DROP vs the last turn means a
# /compact (or /clear) just happened. Re-arm all pings so the sweet spots fire again post-compact.
prev=$(cat "$last_file" 2>/dev/null)
if [ -n "$prev" ] && [ "$prev" -gt 0 ] 2>/dev/null && [ "$ctx" -lt $(( prev * 70 / 100 )) ] 2>/dev/null; then
  for pct in $PCTS; do rm -f "${state_dir}/fibengine-checkpoint-${session}-${pct}" 2>/dev/null; done
fi
printf '%s' "$ctx" > "$last_file" 2>/dev/null

# Pick the HIGHEST crossed-but-unpinged threshold (one ping per turn).
fire=""
for pct in $PCTS; do
  thr=$(( WINDOW_TOKENS * pct / 100 ))
  if [ "$ctx" -ge "$thr" ] 2>/dev/null; then
    [ -f "${state_dir}/fibengine-checkpoint-${session}-${pct}" ] || fire="$pct"
  fi
done
[ -z "$fire" ] && exit 0

# Mark the fired threshold and every lower crossed one, so a jump past several pings only once.
for pct in $PCTS; do
  thr=$(( WINDOW_TOKENS * pct / 100 ))
  if [ "$ctx" -ge "$thr" ] 2>/dev/null && [ "$pct" -le "$fire" ] 2>/dev/null; then
    : > "${state_dir}/fibengine-checkpoint-${session}-${pct}" 2>/dev/null
  fi
done

pct_now=$(( ctx * 100 / WINDOW_TOKENS ))
if [ "$fire" -ge 40 ] 2>/dev/null; then
cat <<MSG
[COMPACT NOW — RELAY TO CHAMOUN] Context is ~${pct_now}% of a 1M window (${ctx} tokens) — past the 400k
hard ceiling Chamoun set. ACTION: (1) make us compact-safe — refresh docs/research_wiki/handoff.md (the six
sections), commit, leave the tree green; (2) in your reply, tell Chamoun IN PLAIN TEXT that we hit 400k and
it is time to run /compact (compaction now required). A hook cannot run /compact — only Chamoun can; your
job is to make it safe and say so to him.
MSG
else
cat <<MSG
[checkpoint reminder — RELAY TO CHAMOUN] Context is ~${pct_now}% of a 1M window (${ctx} tokens) — past the
350k save-point Chamoun set. ACTION: (1) save state — refresh docs/research_wiki/handoff.md (six sections:
Observed/Inferred/Unverified . repo state . constraints . next step), commit, gates green; (2) in your
reply, tell Chamoun the 350k checkpoint fired and state is saved. Next ping at 400k = mandatory compact.
MSG
fi
exit 0
