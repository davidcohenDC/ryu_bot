# Ryubot

[![Build](https://github.com/davidcohenDC/ryubot/actions/workflows/build.yml/badge.svg)](https://github.com/davidcohenDC/ryubot/actions/workflows/build.yml)

A Discord bot for running tournaments, built with `discord.py` around a small
domain/application/infrastructure split so the tournament rules stay testable
independently of Discord.

This is a private, ongoing project — not archived, kept evolving.

## What it does

- Tournament domain model: phases (Swiss, single/double bracket, …), match
  modes (BO1/BO3/BO5) and game formats, with invariants enforced in the
  domain layer (e.g. a tournament needs at least one phase).
- Application layer (use cases + commands/DTOs) that the Discord layer calls
  into, backed by a Unit of Work over SQLModel/SQLAlchemy (async, SQLite by
  default).
- Discord-side permission checks (role/channel gating), reaction-role
  handling and embed helpers for consistent bot messages.

## Run it

You need Docker.

```sh
git clone https://github.com/davidcohenDC/ryubot.git
cd ryubot
cp .env.example .env   # fill in your bot token, guild role/channel IDs, ...
docker compose up --build
```

The SQLite database lives under `./database` and the log file under
`./discord.log` on the host, both mounted into the container so they survive
a restart.

## Develop it

```sh
python -m pip install -r requirements.txt
python -m pytest
```

Tests run without Discord or a real database: `tests/conftest.py` sets
placeholder settings, and the application-layer tests use an in-memory Unit
of Work.

## How it is organised

- `src/domains/` — entities, value objects and repository interfaces (ports).
- `src/application/` — use cases, commands/DTOs, the Unit of Work contract.
- `src/infrastructure/` — SQLModel repositories and Discord-specific adapters
  (permissions, views).
- `src/interfaces/discord/` — cogs wiring Discord commands to the use cases.
- `tests/` — domain and application-layer tests (`pytest`, `pytest-asyncio`).

## Status

The domain and application layers are covered by tests and used by
`src/main.py` as a runnable example. The Discord command layer
(`src/interfaces/discord/cogs/tournament_cog.py`) still targets the
pre-refactor API and needs to be rewired to the current use cases before
tournament commands work end-to-end in Discord; the bot logs and skips it on
startup rather than crashing.
