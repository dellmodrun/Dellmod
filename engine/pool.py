"""The Trench — Benthic's Proof-of-Useful-Compute mining pool.

Miners accrue *shares* equal to their verified work (quality-scaled TFLOP-hours).
When the pool settles an epoch, that epoch's emission is split in proportion to
shares, minus the pool fee, and balances reset (a PPLNS-style scheme applied to
verified compute rather than hashes).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

DEFAULT_FEE: float = 0.015  # 1.5% pool fee -> treasury + verifier rewards


def reward_split(works: Dict[str, float], epoch_emission: float,
                 fee: float = DEFAULT_FEE) -> Dict[str, float]:
    """Split ``epoch_emission`` across miners by verified work (Eq. 3).

    ``works`` maps miner id -> verified, quality-scaled work for the epoch.
    Returns miner id -> reward in $BENTHIC. If no work was done, everyone gets 0.
    """
    if not 0.0 <= fee < 1.0:
        raise ValueError("fee must be in [0, 1)")
    if epoch_emission < 0:
        raise ValueError("epoch_emission must be >= 0")
    total = sum(works.values())
    if total <= 0:
        return {miner: 0.0 for miner in works}
    payable = epoch_emission * (1.0 - fee)
    return {miner: payable * work / total for miner, work in works.items()}


@dataclass
class Pool:
    """Accrues shares across an epoch and settles them into rewards."""

    fee: float = DEFAULT_FEE
    shares: Dict[str, float] = field(default_factory=dict)

    def submit(self, miner: str, verified_work: float) -> None:
        """Credit a miner with verified work for the current epoch."""
        if verified_work < 0:
            raise ValueError("verified_work must be >= 0")
        self.shares[miner] = self.shares.get(miner, 0.0) + verified_work

    def total_work(self) -> float:
        return sum(self.shares.values())

    def settle(self, epoch_emission: float) -> Dict[str, float]:
        """Distribute ``epoch_emission`` and reset share balances."""
        rewards = reward_split(self.shares, epoch_emission, self.fee)
        self.shares = {}
        return rewards
