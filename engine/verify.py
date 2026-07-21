"""Proof-of-Useful-Compute verification game.

Fake work is deterred economically. A fraction ``s`` of jobs are shadowed
(dispatched redundantly) and any result may be challenged with probability
``p_c`` by a verifier who re-runs it. A fabricated result must escape *both*
checks, so its escape probability is:

    P_escape = (1 - s) * (1 - p_c)                      (Eq. 2)

With slashing set above the expected gain from cheating, honest computation is
the unique profitable strategy.
"""
from __future__ import annotations


def _check_prob(name: str, value: float) -> None:
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be in [0, 1]")


def escape_probability(sampling_rate: float, challenge_prob: float) -> float:
    """Probability a fabricated result escapes redundancy *and* challenge."""
    _check_prob("sampling_rate", sampling_rate)
    _check_prob("challenge_prob", challenge_prob)
    return (1.0 - sampling_rate) * (1.0 - challenge_prob)


def expected_cheat_value(gain: float, stake: float,
                         sampling_rate: float, challenge_prob: float) -> float:
    """Expected value of attempting to cheat.

    Cheat pays ``gain`` if it escapes, else the miner is slashed ``stake``.
    """
    if gain < 0 or stake < 0:
        raise ValueError("gain and stake must be >= 0")
    p = escape_probability(sampling_rate, challenge_prob)
    return p * gain - (1.0 - p) * stake


def is_cheating_deterred(gain: float, stake: float,
                         sampling_rate: float, challenge_prob: float) -> bool:
    """True when honest work dominates: E[cheat] <= 0."""
    return expected_cheat_value(gain, stake, sampling_rate, challenge_prob) <= 0.0


def min_stake_to_deter(gain: float, sampling_rate: float,
                       challenge_prob: float) -> float:
    """Minimum stake that makes cheating unprofitable for a given ``gain``."""
    p = escape_probability(sampling_rate, challenge_prob)
    if p >= 1.0:  # no verification at all -> cannot deter with finite stake
        return float("inf")
    return p * gain / (1.0 - p)
