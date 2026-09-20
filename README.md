# Ryu Bot

[![Build](https://github.com/davidcohenDC/ryu_bot/actions/workflows/build.yml/badge.svg)](https://github.com/davidcohenDC/ryu_bot/actions/workflows/build.yml)
[![Release](https://img.shields.io/github/v/release/davidcohenDC/ryu_bot)](https://github.com/davidcohenDC/ryu_bot/releases/latest)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A Discord bot I wrote and ran on my own server to manage Pokémon-style
tournaments: create/update/list them, soft- or hard-delete, and post an
announcement with a button players click to get their entry code by DM.

I keep it here as-is, parked until I next pick it up.

## What it does

- `/tour_create`, `/tour_update`, `/tour_delete`, `/tour_list`,
  `/tour_announce` — one Swiss + Top Cut tournament per Discord server,
  each with a name, an entry code and a running round counter.
- Staff-only, channel-gated commands (`STAFF_ROLE_IDS`, `COMMAND_CHANNEL_IDS`).
- The announcement posts a "Claim Code" button: clicking it DMs the player
  their entry code and shows it ephemerally, so they don't have to ask staff.
- Reaction-role assignment and a handful of permission/embed helpers used
  across the bot.

## Run it

You need Docker.

```sh
git clone https://github.com/davidcohenDC/ryu_bot.git
cd ryu_bot
cp .env.example .env   # bot token, guild role/channel IDs, ...
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

- `src/domains/tournament/{models,services,repositories,exceptions}.py` —
  the tournament feature that is actually wired to Discord: a plain
  dataclass, a service and a raw-SQL `aiosqlite` repository.
- `src/interfaces/discord/cogs/tournament_cog.py`,
  `src/infrastructure/discord/views/claim_code_view.py` — the commands and
  the claim-code button.
- `src/domains/tournament/entities/`, `src/application/`,
  `src/infrastructure/persistence/sqlmodel/` — a richer, multi-phase
  tournament domain (SQLModel/SQLAlchemy, use cases, DTOs) from an
  in-progress rewrite. It's tested and runnable on its own
  (`src/main.py`), but **not** wired to the Discord commands yet — the two
  live side by side for now.
- `tests/` — covers both: the domain/application layer above, and (via
  `tests/conftest.py`) whatever needs the bot's settings to import cleanly.

## Since 2025

The tournament feature above — the part that ran on my server — is
untouched. In 2026 I moved the repository here, fixed the Docker entrypoint
and the bot startup (both were broken in every commit: the entrypoint
pointed at a file that didn't exist, and `bot.py` never actually called
`bot.run()`), added CI and semantic-release, and archived it.

## License

[MIT](LICENSE) © 2025 David Cohen
