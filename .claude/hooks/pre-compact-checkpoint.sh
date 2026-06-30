#!/usr/bin/env bash
# UserPromptSubmit hook: ping ONCE when the context window crosses the sweet spot, so a checkpoint
# happens IN TIME — before thread-drift/compaction loses detail. The EARLY trigger; model-discretion
# invocation of /pre-compact-checkpoint proved unreliable (docs/research_wiki/log.md 2026-06-30).
#
# Sweet spot = CONTEXT_THRESHOLD tokens (~25% of a 1M window = 250k). Tune the one constant below;
# lower it on a smaller-window model. The figure is READ from the transcript's latest usage
# (input + cache_read + cache_creation = tokens actually sent = current window occupancy) — the same
# number /context shows, not a turn-count guess.
#
# A hook can only REMIND, never invoke a skill. Fires once per session (temp state file). SONAR: pure
# bash + perl (Git Bash core, JSON::PP) — never python.exe / powershell.exe. exit 0 always (never blocks).

set -o pipefail
CONTEXT_THRESHOLD=250000   # sweet spot: ~25% of a 1M window — the moment to checkpoint

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
[ "$ctx" -lt "$CONTEXT_THRESHOLD" ] 2>/dev/null && exit 0

# Ping once per session.
state_dir="${TEMP:-${TMPDIR:-/tmp}}"
state="${state_dir}/fibengine-checkpoint-pinged-${session}"
[ -f "$state" ] && exit 0
: > "$state" 2>/dev/null

pct=$(( ctx * 100 / 1000000 ))
cat <<MSG
[checkpoint reminder] Context is ~${pct}% of a 1M window (${ctx} tokens) — at the sweet spot.
Run /pre-compact-checkpoint now: capture Observed / Inferred / Unverified + repo state + user
constraints + next smallest safe step, refresh docs/research_wiki/handoff.md, and leave the tree green.
This fires once per session — you will not be nagged again.
MSG
exit 0
