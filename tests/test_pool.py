import pytest

from engine.pool import Pool, reward_split


def test_split_is_proportional_to_work():
    out = reward_split({"a": 30.0, "b": 10.0}, epoch_emission=100.0, fee=0.0)
    assert out["a"] == pytest.approx(75.0)
    assert out["b"] == pytest.approx(25.0)


def test_fee_is_withheld():
    out = reward_split({"a": 1.0}, epoch_emission=100.0, fee=0.015)
    assert out["a"] == pytest.approx(98.5)


def test_total_paid_never_exceeds_emission():
    out = reward_split({"a": 3.0, "b": 5.0, "c": 2.0}, epoch_emission=100.0, fee=0.015)
    assert sum(out.values()) == pytest.approx(98.5)


def test_zero_work_pays_zero():
    out = reward_split({"a": 0.0, "b": 0.0}, epoch_emission=100.0)
    assert out == {"a": 0.0, "b": 0.0}


def test_pool_accrues_and_resets_on_settle():
    p = Pool(fee=0.0)
    p.submit("a", 10.0)
    p.submit("a", 5.0)
    p.submit("b", 15.0)
    assert p.total_work() == pytest.approx(30.0)
    rewards = p.settle(epoch_emission=60.0)
    assert rewards["a"] == pytest.approx(30.0)
    assert rewards["b"] == pytest.approx(30.0)
    assert p.total_work() == 0.0  # balances reset


def test_invalid_fee_raises():
    with pytest.raises(ValueError):
        reward_split({"a": 1.0}, 100.0, fee=1.0)
