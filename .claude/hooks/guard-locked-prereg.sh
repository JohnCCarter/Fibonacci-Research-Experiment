#!/usr/bin/env bash
# PreToolUse guard: ask before editing a LOCKED pre-registration file.
#
# A locked prereg carries the sentinel `<!-- prereg:locked -->`. This file must stay immutable
# after sign-off so a result can never be edited against its own registration; post-lock material
# belongs in the `*-postlock.md` sibling. The guard returns permissionDecision "ask" (not "deny"):
# it breaks the silence on an accidental edit without hard-locking out a deliberate one.
#
# Cost discipline (SONAR): fires on every Edit|Write, but the cheap `case` pre-filter exits with
# zero subprocesses unless the payload even mentions `-prereg-`. perl (Git Bash core, JSON::PP) is
# spawned only in that rare case — never `python.exe`/`powershell.exe`.
#
# Fail modes (kept distinct on purpose):
#   - sentinel ABSENT  -> file is not locked            -> fail-OPEN  (allow)
#   - grep ERRORS while checking a confirmed prereg file -> fail-CLOSED (ask)

set -o pipefail
input=$(cat)

# Pre-filter: no mention of a prereg file anywhere in the payload -> not our concern, spawn nothing.
case "$input" in
  *-prereg-*) ;;
  *) exit 0 ;;
esac

# Structured extraction of ONLY tool_input.file_path. Raw-grep would false-match on old/new_string
# content, so use a real JSON parser. Empty result (parse failure / no path) -> fail-open.
fp=$(perl -MJSON::PP -0777 -ne '
  my $j = eval { decode_json($_) };
  exit 0 unless $j && ref $j eq "HASH";
  my $ti = $j->{tool_input};
  print $ti->{file_path} if ref $ti eq "HASH" && defined $ti->{file_path};
' <<<"$input" 2>/dev/null)
[ -z "$fp" ] && exit 0

# Normalise to a bash-readable path (C:\... -> /c/...).
fp_unix=$(cygpath -u "$fp" 2>/dev/null) || fp_unix=$(printf '%s' "$fp" | sed 's#\\#/#g')

# Scope: only guard prereg review files, and never the unguarded postlock sibling.
case "$fp_unix" in
  *-postlock.md) exit 0 ;;
  */research_wiki/reviews/*-prereg-*.md) ;;
  *) exit 0 ;;
esac

# A path that doesn't exist yet is a new file being created -> cannot be locked -> allow.
[ -f "$fp_unix" ] || exit 0

ask() {
  printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"ask","permissionDecisionReason":"Locked pre-registration (immutable after sign-off). Post-lock material belongs in the *-postlock.md sibling. Confirm only if you intend to edit the registration itself."}}'
  exit 0
}

grep -q 'prereg:locked' "$fp_unix" 2>/dev/null
case "$?" in
  0) ask ;;     # locked -> ask
  1) exit 0 ;;  # not locked -> fail-open (allow)
  *) ask ;;     # grep error while guarding a prereg file -> fail-closed (ask)
esac
