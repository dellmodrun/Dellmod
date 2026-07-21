"""$BENTHIC emission schedule.

Emission is *disinflationary*: a fixed number of tokens is minted per epoch,
halving every ``HALVING`` epochs so that early network growth is well rewarded
while total mined supply converges to a hard cap.

    E(t) = E0 * 2 ** (-floor(t / H))

The geometric series sums to a finite cap ``2 * E0 * H`` regardless of how fast
the network grows.
"""
from __future__ import annotations

# --- protocol constants (preview; subject to community calibration) ----------
DEFAULT_E0: float = 20_000.0       # $BENTHIC minted per epoch during era 1
DEFAULT_HALVING: int = 25_000      # epochs per era (~2.85 years at 1-hour epochs)
# -> hard cap = 2 * E0 * H = 1,000,000,000 BENTHIC


def era(epoch: int, halving: int = DEFAULT_HALVING) -> int:
    """Return the halving era (0-indexed) that ``epoch`` falls in."""
    if epoch < 0:
        raise ValueError("epoch must be >= 0")
    return epoch // halving


def emission(epoch: int, e0: float = DEFAULT_E0, halving: int = DEFAULT_HALVING) -> float:
    """Per-epoch emission at ``epoch`` (Eq. 4 in the whitepaper)."""
    return e0 / (2 ** era(epoch, halving))


def cumulative_supply(epoch: int, e0: float = DEFAULT_E0,
                      halving: int = DEFAULT_HALVING) -> float:
    """Total $BENTHIC minted over epochs ``[0, epoch)``."""
    if epoch < 0:
        raise ValueError("epoch must be >= 0")
    full_eras = epoch // halving
    total = sum(halving * (e0 / 2 ** k) for k in range(full_eras))
    total += (epoch - full_eras * halving) * (e0 / 2 ** full_eras)
    return total


def max_supply(e0: float = DEFAULT_E0, halving: int = DEFAULT_HALVING) -> float:
    """Hard cap on mined supply: the limit of the geometric series."""
    return 2.0 * e0 * halving


if __name__ == "__main__":  # pragma: no cover
    print(f"era-1 emission/epoch : {emission(0):,.2f} BENTHIC")
    print(f"era-2 emission/epoch : {emission(DEFAULT_HALVING):,.2f} BENTHIC")
    print(f"max mined supply     : {max_supply():,.0f} BENTHIC")
