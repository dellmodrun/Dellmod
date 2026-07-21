import pytest

from engine import emission


def test_era_one_emission_is_e0():
    assert emission.emission(0) == emission.DEFAULT_E0


def test_emission_halves_each_era():
    h = emission.DEFAULT_HALVING
    assert emission.emission(h) == pytest.approx(emission.DEFAULT_E0 / 2)
    assert emission.emission(2 * h) == pytest.approx(emission.DEFAULT_E0 / 4)


def test_era_index():
    h = emission.DEFAULT_HALVING
    assert emission.era(0) == 0
    assert emission.era(h - 1) == 0
    assert emission.era(h) == 1


def test_max_supply_is_geometric_limit():
    assert emission.max_supply() == pytest.approx(2 * emission.DEFAULT_E0 * emission.DEFAULT_HALVING)


def test_cumulative_supply_converges_to_cap():
    cap = emission.max_supply()
    minted = emission.cumulative_supply(emission.DEFAULT_HALVING * 40)
    assert minted < cap
    assert minted > 0.99 * cap  # after 40 eras we are within 1% of the cap


def test_cumulative_first_era_is_linear():
    h = emission.DEFAULT_HALVING
    assert emission.cumulative_supply(h) == pytest.approx(emission.DEFAULT_E0 * h)


def test_negative_epoch_raises():
    with pytest.raises(ValueError):
        emission.emission(-1)
