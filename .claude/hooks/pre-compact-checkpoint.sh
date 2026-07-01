#!/usr/bin/env bash
# UserPromptSubmit hook: ping when EITHER trigger fires first, so a checkpoint happens IN TIME —
# before thread-drift/compaction loses detail. Model-discretion invocation proved unreliable
# (docs/research_wiki/log.md 2026-06-30).
#
#   (a) CAPACITY — the context window crosses a token sweet-spot. PCTS="35 40" of a 1M window
#       (350k save-point, 400k MUST-compact; Chamoun's thresholds). Catches token-heavy sessions.
#   (b) ACTIVITY — the session crosses a user-TURN threshold. TURNS="15 30" prompts since session
#       start / last compact. Catches SPRAWLING but token-LIGHT sessions: many topic switches at low
#       % (thread-health drift, invisible to /context). Added 2026-07-01 after a 24-prompt / 27.5%
#       session drifted 7+ topic switches with NO capacity ping (correct — window was fine; but a
#       checkpoint was due on thread-health grounds). The skill's own rule: "two triggers, whichever
#       fires first — and the first is usually NOT the percentage."
#
# The fired ping is RELAYED to Chamoun by the agent (a hook can't post to his chat) — the message tells
# the agent to relay it AS THE FIRST LINE so it can't be soft-pedaled. Each threshold pings AT MOST ONCE
# per session; a jump past several pings only the highest. A /compact or /clear (detected as a big ctx
# drop vs the last turn) RE-ARMS both ladders + resets the turn counter, so they fire again post-compact.
# Tune PCTS / TURNS / WINDOW_TOKENS below (reason in %, not absolute tokens; lower on a smaller-window model).
# Capacity is READ from the transcript's latest usage (input + cache_read + cache_creation = tokens
# actually sent = current window occupancy) — the same number /context shows.
#
# A hook can only REMIND, never invoke a skill. SONAR: pure bash + perl (Git Bash core, JSON::PP) —
# never python.exe / powershell.exe. exit 0 always (never blocks).

set -o pipefail
WINDOW_TOKENS=1000000
PCTS="35 40"               # capacity: 350k save-point, 400k = MUST-compact (% of 1M)
TURNS="15 30"              # activity: user-prompts since session start / last compact (thread-health)

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
turn_file="${state_dir}/fibengine-checkpoint-turns-${session}"

# Compaction reset: ctx only ever grows within a session, so a big DROP vs the last turn means a
# /compact (or /clear) just happened. Re-arm BOTH ladders + reset the turn counter so the sweet spots
# fire again post-compact.
compacted=0
prev=$(cat "$last_file" 2>/dev/null)
if [ -n "$prev" ] && [ "$prev" -gt 0 ] 2>/dev/null && [ "$ctx" -lt $(( prev * 70 / 100 )) ] 2>/dev/null; then
  compacted=1
  for pct in $PCTS; do rm -f "${state_dir}/fibengine-checkpoint-${session}-${pct}" 2>/dev/null; done
  for t in $TURNS; do rm -f "${state_dir}/fibengine-checkpoint-turn-${session}-${t}" 2>/dev/null; done
  rm -f "$turn_file" 2>/dev/null
fi
printf '%s' "$ctx" > "$last_file" 2>/dev/null

# Increment the user-turn counter (this hook fires once per user prompt). Reset if we just compacted.
prev_turns=$(cat "$turn_file" 2>/dev/null)
[ "$compacted" = 1 ] && prev_turns=0
case "$prev_turns" in ''|*[!0-9]*) prev_turns=0 ;; esac
turns=$(( prev_turns + 1 ))
printf '%s' "$turns" > "$turn_file" 2>/dev/null

# --- CAPACITY: pick the HIGHEST crossed-but-unpinged pct threshold (one ping per turn) ---
fire=""
for pct in $PCTS; do
  thr=$(( WINDOW_TOKENS * pct / 100 ))
  if [ "$ctx" -ge "$thr" ] 2>/dev/null; then
    [ -f "${state_dir}/fibengine-checkpoint-${session}-${pct}" ] || fire="$pct"
  fi
done
if [ -n "$fire" ]; then
  for pct in $PCTS; do
    thr=$(( WINDOW_TOKENS * pct / 100 ))
    if [ "$ctx" -ge "$thr" ] 2>/dev/null && [ "$pct" -le "$fire" ] 2>/dev/null; then
      : > "${state_dir}/fibengine-checkpoint-${session}-${pct}" 2>/dev/null
    fi
  done
fi

# --- ACTIVITY: pick the HIGHEST crossed-but-unpinged turn threshold ---
fire_turn=""
for t in $TURNS; do
  if [ "$turns" -ge "$t" ] 2>/dev/null; then
    [ -f "${state_dir}/fibengine-checkpoint-turn-${session}-${t}" ] || fire_turn="$t"
  fi
done
if [ -n "$fire_turn" ]; then
  for t in $TURNS; do
    if [ "$turns" -ge "$t" ] 2>/dev/null && [ "$t" -le "$fire_turn" ] 2>/dev/null; then
      : > "${state_dir}/fibengine-checkpoint-turn-${session}-${t}" 2>/dev/null
    fi
  done
fi

pct_now=$(( ctx * 100 / WINDOW_TOKENS ))

# Capacity takes priority (it is the harder ceiling); else the thread-health turn ping.
if [ "$fire" = "40" ] 2>/dev/null; then
cat <<MSG
⚠️ [RELAY TO CHAMOUN AS YOUR FIRST LINE] COMPACT NOW — context ~${pct_now}% of a 1M window (${ctx} tokens),
past the 400k hard ceiling Chamoun set. WHY NOW: capacity ceiling. ACTION: (1) make us compact-safe —
refresh docs/research_wiki/handoff.md (the six sections), commit, leave the tree green; (2) tell Chamoun
IN PLAIN TEXT that we hit 400k and it is time to run /compact (only he can — a hook cannot).
MSG
elif [ -n "$fire" ]; then
cat <<MSG
⚠️ [RELAY TO CHAMOUN AS YOUR FIRST LINE] CHECKPOINT — context ~${pct_now}% of a 1M window (${ctx} tokens),
past the 350k save-point Chamoun set. WHY NOW: capacity save-point. ACTION: (1) save state — refresh
docs/research_wiki/handoff.md (six sections: Observed/Inferred/Unverified · repo state · constraints ·
next step), commit, gates green; (2) tell Chamoun the 350k checkpoint fired and state is saved. Next ping
at 400k = mandatory compact.
MSG
elif [ -n "$fire_turn" ]; then
cat <<MSG
⚠️ [RELAY TO CHAMOUN AS YOUR FIRST LINE] CHECKPOINT (thread-health) — ${turns} user-turns this session,
capacity only ~${pct_now}% (${ctx} tokens). WHY NOW: long/sprawling session — drift risk (topic switches,
stale tool-output, re-deriving settled points) sets in BEFORE the capacity %, and is invisible to /context.
ACTION: run /pre-compact-checkpoint — refresh docs/research_wiki/handoff.md (six sections) AND re-anchor to
the live task; tell Chamoun the turn checkpoint fired. Capacity is fine — this is purely thread health.
MSG
else
  exit 0
fi
exit 0
