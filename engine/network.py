"""Miner / network model and the telemetry snapshot builder.

`build_snapshot()` returns the JSON object the web dashboard consumes. It is
deterministic (no randomness), so the same ``as_of`` date always yields the same
snapshot — reproducible telemetry for the preview dashboard. Once the network is
live, this module is replaced by a real aggregator over on-chain epoch reports;
the *shape* of the output stays the same.
"""
from __future__ import annotations

import datetime
import math
from dataclasses import dataclass
from typing import Dict, List, Optional

from . import emission, pool

WINDOW = 30  # epochs shown in the trailing charts


@dataclass(frozen=True)
class Miner:
    """A compute provider and its epoch contribution."""
    id: str
    tflops: float
    quality: float = 1.0
    online: bool = True

    @property
    def verified_work(self) -> float:
        """Quality-scaled work used for reward accounting."""
        return self.tflops * self.quality


# Preview miner set (deep-sea themed handles). Replaced by live discovery.
_MINERS: List[Miner] = [
    Miner("abyss.bnth", 6120, 0.99),
    Miner("kraken-07", 4980, 0.98),
    Miner("mariana.eth", 3910, 0.99),
    Miner("nautilus", 3120, 0.97),
    Miner("deepcurrent", 2670, 0.98),
    Miner("tentacle.io", 2040, 0.94, online=False),
    Miner("benthos-lab", 1610, 0.96),
]

_POOLS = [
    ("Abyssal Pool", 0.34, "#f65e06"),
    ("Trench Collective", 0.27, "#ff8a3d"),
    ("Solo divers", 0.21, "#ffb885"),
    ("Reef Syndicate", 0.18, "#b5471a"),
]


def _phase(compute_index: float) -> str:
    if compute_index >= 82:
        return "Steady"
    if compute_index >= 45:
        return "Expansion"
    return "Bootstrap"


def _compute_series(n: int = WINDOW) -> List[float]:
    """Deterministic, organic-looking compute-index series (uptrending)."""
    out = []
    for i in range(n):
        base = 40 + 34 * (i / (n - 1))
        wobble = 6 * math.sin(i * 0.9) + 3 * math.sin(i * 2.3)
        out.append(round(max(5.0, min(97.0, base + wobble)), 1))
    out[-1] = 73.0
    return out


def current_epoch(as_of: datetime.date, genesis: datetime.date) -> int:
    """Hours since genesis == epoch index (1-hour epochs)."""
    return max(0, (as_of - genesis).days * 24)


def build_snapshot(as_of: Optional[datetime.date] = None) -> Dict:
    """Assemble the dashboard telemetry object."""
    as_of = as_of or datetime.date.today()
    genesis = datetime.date(2026, 5, 1)
    epoch = current_epoch(as_of, genesis) or 1

    dates = [(as_of - datetime.timedelta(days=(WINDOW - 1 - i))).isoformat()
             for i in range(WINDOW)]
    compute = _compute_series()
    price = [round(0.008 * (1 + 0.9 * (c / 100)) + 0.0006 * math.sin(i * 1.3), 4)
             for i, c in enumerate(compute)]
    history = ["h" if c >= 68 else "m" if c >= 48 else "l" for c in compute]

    compute_index = int(round(compute[-1]))
    total_tflops = sum(m.tflops for m in _MINERS) * 6.5  # scale to full network
    epoch_emission = emission.emission(epoch)

    # reward split across the leaderboard, consistent with pool economics
    works = {m.id: m.verified_work for m in _MINERS}
    rewards = pool.reward_split(works, epoch_emission, pool.DEFAULT_FEE)
    leaderboard = [{
        "miner": m.id,
        "tflops": m.tflops,
        "share": round(m.verified_work / total_tflops, 3),
        "reward": f"{rewards[m.id] / 1000:.1f}k",
        "status": "online" if m.online else "idle",
    } for m in _MINERS]

    minted = emission.cumulative_supply(epoch)
    cap = emission.max_supply()

    return {
        "as_of": as_of.isoformat(),
        "window_days": WINDOW,
        "compute_index": compute_index,
        "phase": _phase(compute_index),
        "phase_probs": {"bootstrap": 0.11, "expansion": 0.72, "steady": 0.17},
        "network": {
            "active_miners": 1284,
            "tflops": int(total_tflops),
            "mined_epoch": int(epoch_emission),
            "reward_per_tflop": 0.42,
            "jobs_verified": 92140,
            "verify_rate": 0.994,
        },
        "drivers": [
            {"k": "Active miners", "v": "1,284", "note": "+8.2% · 24h", "tone": "good"},
            {"k": "Network compute", "v": f"{total_tflops/1000:.1f} PFLOPs", "note": "+5.1% · 24h", "tone": "good"},
            {"k": "Verified-job rate", "v": "99.4%", "note": "nominal", "tone": "good"},
            {"k": "Reward / TFLOP·h", "v": "0.42 BENTHIC", "note": "−1.3% · 24h", "tone": "bad"},
            {"k": "Pool queue depth", "v": "3.1k jobs", "note": "steady", "tone": "neu"},
        ],
        "compute_chart": {"dates": dates, "compute": compute, "price": price},
        "pool_dist": [{"label": n, "share": s, "color": c} for n, s, c in _POOLS],
        "leaderboard": leaderboard,
        "history": history,
        "phase_stats": {
            "Bootstrap": {"util": 0.31, "reward": 0.61, "share": 19, "dur": 8},
            "Expansion": {"util": 0.68, "reward": 0.42, "share": 57, "dur": 21},
            "Steady": {"util": 0.86, "reward": 0.28, "share": 24, "dur": 34},
        },
        "token": {
            "symbol": "BENTHIC",
            "max_supply": f"{cap:,.0f}",
            "circulating": "142,600,000",
            "mined_pct": round(minted / cap * 100, 1),
            "emission_epoch": f"{epoch_emission:,.0f}",
            "next_halving": f"epoch {emission.DEFAULT_HALVING:,}",
        },
        "params": {
            "chain": "Robinhood Chain (L2)",
            "contract": "not deployed · preview",
            "epoch": "1 h",
            "work": "Proof of Useful Compute",
            "verification": "redundant + challenge",
            "pool_fee": "1.5%",
        },
        "feed": [
            {"epoch": f"{dates[-1]} · {14 - i:02d}:00",
             "phase": _phase(compute[-1 - i]),
             "compute": f"{(total_tflops * compute[-1 - i] / compute[-1]) / 1000:.1f} PF",
             "miners": 1284 - i * 13,
             "mined": f"{epoch_emission / 1000:.1f}k",
             "status": "finalized"}
            for i in range(6)
        ],
    }
