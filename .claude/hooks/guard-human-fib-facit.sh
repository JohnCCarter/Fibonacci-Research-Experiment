#!/usr/bin/env bash
# PreToolUse guard: ask before an agent edits or creates HUMAN FIB FACIT.
#
# `data/labels/human_fib/**/fib_*.json` is ground truth — the human draws it via the labeling tool
# ("Human fib = facit"; no auto-fib as truth, AGENTS.md §2). An agent hand-writing or editing these
# is almost always a mistake, so the guard breaks the silence with permissionDecision "ask" (not
# "deny"): a deliberate, sanctioned correction still goes through on confirm.
#
# Scope: ONLY base `fib_*.json` facit is guarded. Regenerable `*_events.json` / `*_interactions.csv`
# are NOT facit and are left alone. The labeling GUI is a separate process — unaffected; this only
# ever sees Claude's own Edit/Write tool calls.
#
# Cost discipline (SONAR): the cheap `case` pre-filter exits with zero subprocesses unless the
# payload even mentions `human_fib`. perl (Git Bash core, JSON::PP) spawns only in that case —
# never `python.exe` / `powershell.exe`.

set -o pipefail
input=$(cat)

# Pre-filter: nothing about human_fib in the payload -> not our concern, spawn nothing.
case "$input" in
  *human_fib*) ;;
  *) exit 0 ;;
esac

# Structured extraction of ONLY tool_input.file_path (raw-grep would false-match on file content).
fp=$(perl -MJSON::PP -0777 -ne '
  my $j = eval { decode_json($_) };
  exit 0 unless $j && ref $j eq "HASH";
  my $ti = $j->{tool_input};
  print $ti->{file_path} if ref $ti eq "HASH" && defined $ti->{file_path};
' <<<"$input" 2>/dev/null)
[ -z "$fp" ] && exit 0

# Normalise to a bash-readable path (C:\... -> /c/...).
fp_unix=$(cygpath -u "$fp" 2>/dev/null) || fp_unix=$(printf '%s' "$fp" | sed 's#\\#/#g')

# Scope: only base fib_*.json facit under human_fib. Exclude regenerable `*_events.json` FIRST
# (the fib_*.json glob would otherwise catch fib_<id>_events.json); interactions are .csv, not matched.
case "$fp_unix" in
  */data/labels/human_fib/*/*_events.json) exit 0 ;;
  */data/labels/human_fib/*/fib_*.json) ;;
  *) exit 0 ;;
esac

printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"ask","permissionDecisionReason":"This is human-drawn fib FACIT (ground truth, authored via the labeling tool; AGENTS.md: Human fib = facit, no auto-fib as truth). Agents should not hand-edit facit. Confirm only if this is a deliberate, sanctioned correction."}}'
exit 0
