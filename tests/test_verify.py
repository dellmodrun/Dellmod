import pytest

from engine import verify


def test_escape_probability_bounds():
    assert verify.escape_probability(0.0, 0.0) == 1.0   # no checks -> always escapes
    assert verify.escape_probability(1.0, 0.0) == 0.0   # full redundancy -> never
    assert verify.escape_probability(0.5, 0.5) == pytest.approx(0.25)


def test_more_verification_lowers_escape():
    low = verify.escape_probability(0.1, 0.1)
    high = verify.escape_probability(0.6, 0.6)
    assert high < low


def test_cheating_deterred_when_stake_high():
    # small gain, large stake, decent verification -> not worth cheating
    assert verify.is_cheating_deterred(gain=100, stake=10_000,
                                       sampling_rate=0.3, challenge_prob=0.3)


def test_cheating_pays_without_verification():
    assert not verify.is_cheating_deterred(gain=100, stake=10,
                                           sampling_rate=0.0, challenge_prob=0.0)


def test_min_stake_deters_at_boundary():
    gain = 1000.0
    s, pc = 0.4, 0.4
    stake = verify.min_stake_to_deter(gain, s, pc)
    # at exactly the minimum stake, expected value is ~0 (indifferent)
    ev = verify.expected_cheat_value(gain, stake, s, pc)
    assert ev == pytest.approx(0.0, abs=1e-9)


def test_probability_out_of_range_raises():
    with pytest.raises(ValueError):
        verify.escape_probability(1.5, 0.2)
