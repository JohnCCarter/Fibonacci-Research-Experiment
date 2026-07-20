"""Gated entry point for an ML selection ranker + Optuna tuning (Issue #42 — DEFERRED by design).

Why this is a gate, not a model. The geometric-feature campaign already showed a ranker adds
nothing over prominence on the only powered cell (`no_pivot_signal_above_prominence`, AP 0.057),
and today's structural+empirical checks put the positive selection rule off the geometric axis.
Optuna cannot manufacture signal the features lack — on a data-thin corpus it magnifies noise and
manufactures a false positive, which is exactly what this repo's leakage discipline exists to stop.

So ML/Optuna stay **disabled** until three conditions hold (checked here, fail-closed):
  1. the optional ``[ml]`` extra is installed (scikit-learn / optuna / joblib), AND
  2. there are ``>= MIN_HUMAN_WINDOWS`` real ``created_by: human`` annotation windows (fixtures
     never count — a tuned model on scaffolding is meaningless), AND
  3. a separately pre-registered locked holdout exists (passed in explicitly; no inline invention).

Until then the deterministic ``selection_baseline`` is the ranker of record. This is the honest v0
posture agreed with the owner, logged so the gate is visible, not silently skipped.
"""

from __future__ import annotations

from fibengine.research.selection_annotation import AnnotationWindow

# Data-thin gate: daily facit is N~76 windows-worth at most; a tuned sklearn model below this is
# overfitting, not learning. Deliberately conservative; revisit only with a fresh prereg.
MIN_HUMAN_WINDOWS = 30


class SelectionLearnerGated(RuntimeError):
    """Raised when ML/Optuna is requested before its data / dependency / prereg gate is met."""


def ml_available() -> bool:
    """True iff the optional ``[ml]`` extra is importable. Never imports at module load."""
    try:
        import optuna  # noqa: F401
        import sklearn  # noqa: F401
    except ImportError:
        return False
    return True


def check_gate(windows: list[AnnotationWindow], *, locked_holdout: object | None = None) -> None:
    """Fail-closed gate. Raises unless deps + human windows + a locked holdout are all present."""
    if not ml_available():
        raise SelectionLearnerGated(
            "ML ranker gated: install the optional extra — `uv sync --extra ml` "
            "(scikit-learn, optuna, joblib)."
        )
    n_human = sum(1 for w in windows if w.is_human)
    if n_human < MIN_HUMAN_WINDOWS:
        raise SelectionLearnerGated(
            f"ML ranker gated: need >= {MIN_HUMAN_WINDOWS} human annotation windows, "
            f"have {n_human} (fixtures do not count). Capture contrastive annotations first."
        )
    if locked_holdout is None:
        raise SelectionLearnerGated(
            "ML ranker gated: pass a pre-registered locked holdout — no inline split invention "
            "(repo leakage discipline)."
        )


def fit_ranker(windows: list[AnnotationWindow], *, locked_holdout: object | None = None) -> object:
    """Deferred. Checks the gate first; the functional sklearn ranker is intentionally not built
    in v0 (would beg the very null the gate protects)."""
    check_gate(windows, locked_holdout=locked_holdout)
    raise NotImplementedError(
        "Functional ML ranker deferred: gate passed, but v0 stops here by design. Register a "
        "ranker prereg (baseline-beating decision rule) before building it."
    )


def tune_with_optuna(
    windows: list[AnnotationWindow], *, locked_holdout: object | None = None
) -> object:
    """Deferred Optuna tuning stub. Disabled unless the gate passes; tuning itself is unbuilt."""
    check_gate(windows, locked_holdout=locked_holdout)
    raise NotImplementedError(
        "Optuna tuning deferred: only against selection metrics on a locked holdout, per a fresh "
        "prereg — never inline."
    )
