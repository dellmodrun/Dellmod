"""Benthic — reference engine for Proof-of-Useful-Compute mining.

This package is the backend for the Benthic network: the economic primitives
(emission schedule, pool reward split, verification game) plus a telemetry
builder that produces the JSON consumed by the web dashboard.

Modules
-------
- :mod:`engine.emission` — disinflationary $BENTHIC emission with halving eras.
- :mod:`engine.pool`     — the Trench mining pool: verified-work share accounting.
- :mod:`engine.verify`   — the Proof-of-Useful-Compute verification game.
- :mod:`engine.network`  — miner/network model and telemetry snapshot builder.
- :mod:`engine.pipeline` — writes ``data.json`` for the dashboard.
- :mod:`engine.server`   — a small HTTP server for the site + JSON API.
"""

__version__ = "0.1.0"
__all__ = ["emission", "pool", "verify", "network", "pipeline"]
