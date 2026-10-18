# Contributing to Dellmod

Thanks for your interest in Dellmod 🐙 — contributions are welcome.

## Getting started

```bash
git clone https://github.com/dellmodrun/Dellmod.git
cd Dellmod
python -m pip install -r requirements.txt
python -m pytest -q          # run the test suite
python -m engine.server      # serve the site + API at http://localhost:8777
```

## Ground rules

- **Keep the runtime dependency-free.** The engine and server use only the
  Python standard library; please don't add runtime dependencies without a
  strong reason.
- **Tests pass and cover new logic.** Economic primitives (emission, pool,
  verification) must stay covered — see `tests/`.
- **Small, focused pull requests.** One concern per PR, with a clear title.
- **Match the style** of the surrounding code.

## Reporting issues

Open a GitHub issue with steps to reproduce, expected vs. actual behaviour, and
your environment. Security-sensitive reports: email **GitHub Issues**
instead of filing a public issue.

## Scope note

Dellmod is pre-launch. The mining network, settlement programs and parameters
described in the whitepaper are design targets under active development. The
dashboard currently shows clearly-labelled sample telemetry.
