# Dellmod — reference engine + static site.
# Tiny image: stdlib-only server, no third-party runtime deps.
FROM python:3.12-slim

LABEL org.opencontainers.image.title="Dellmod" \
      org.opencontainers.image.description="Proof-of-Useful-Compute mining for AI, settled on Solana." \
      org.opencontainers.image.source="https://github.com/nuttumrunit/Dellmod" \
      org.opencontainers.image.url="https://nuttumrunit.github.io/Dellmod/" \
      org.opencontainers.image.licenses="MIT"

WORKDIR /app
COPY . /app

# Pre-build the dashboard telemetry so the static site has data on first load.
RUN python -m engine.pipeline

EXPOSE 8777
ENV PORT=8777
CMD ["python", "-m", "engine.server"]
