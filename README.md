# Ryu Bot

[![Build](https://github.com/davidcohenDC/ryu_bot/actions/workflows/build.yml/badge.svg)](https://github.com/davidcohenDC/ryu_bot/actions/workflows/build.yml)
[![Release](https://img.shields.io/github/v/release/davidcohenDC/ryu_bot)](https://github.com/davidcohenDC/ryu_bot/releases/latest)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A Discord bot I wrote and ran on my own server to manage Pokémon-style
tournaments: create/update/list them, soft- or hard-delete, and post an
announcement with a button players click to get their entry code by DM.

I keep it here as-is, parked until I next pick it up.

## What it does

- `/tour_create`, `/tour_update`, `/tour_delete`, `/tour_list` and
  `/tour_announce` manage one Swiss + Top Cut tournament per Discord server,
  each with a name, an entry code and a running round counter.
- Staff-only, channel-gated commands (`STAFF_ROLE_IDS`, `COMMAND_CHANNEL_IDS`).
- The announcement posts a "Claim Code" button: clicking it DMs the player
  their entry code and shows it ephemerally, so they don't have to ask staff.
  The button is only registered for the process that posted it, so it stops
  responding across a bot restart until you run `/tour_announce` again.
- A handful of permission and embed helpers used across the bot.
- `src/utils/reactions.py` and `src/utils/roles.py` have reaction-role
  promotion/demotion logic, but nothing calls them and no listener is
  registered, so today they're dead code, not a working feature.

## Run it on an actual Discord server

Docker builds and starts the process, but getting it to actually respond in
your server needs a few steps on the Discord side first.

1. Go to the [Developer Portal](https://discord.com/developers/applications)
   and create an application, then add a Bot to it. Copy its token, you'll
   need it for `TOKEN` below.
2. On the Bot page, turn on the three privileged gateway intents: Message
   Content, Server Members and Presence. The code asks for all three at
   startup, and Discord rejects the connection if they're off.
3. Under OAuth2 > URL Generator, check the `bot` and `applications.commands`
   scopes, and under bot permissions at least Send Messages, Embed Links and
   Read Message History. Open the generated URL and invite the bot to your
   server.
4. In Discord itself, turn on Developer Mode (User Settings > Advanced) so
   you can right-click any role, channel or message and Copy ID.
5. Clone the repo and fill in `.env`:

   ```sh
   git clone https://github.com/davidcohenDC/ryu_bot.git
   cd ryu_bot
   cp .env.example .env
   ```

   The settings that actually do something for the tournament feature:

   | Setting | What it is |
   |---|---|
   | `TOKEN` | the bot token from step 1 |
   | `PREFIX` | text-command prefix, e.g. `!` (slash commands work either way) |
   | `STAFF_ROLE_IDS` | role ID(s) allowed to run `/tour_*` commands |
   | `COMMAND_CHANNEL_IDS` | channel ID(s) where those commands can be used |
   | `CODE_CHANNEL_ID` | channel where `/tour_announce` posts the entry-code button |

   Every other setting in `.env.example` is required by `Settings` at
   startup (it raises if any are missing) but isn't read by anything the
   bot currently does: `RULE_REACTION_ID`, `RR_MESSAGE_ID`,
   `RYUZEN_TEAM_ROLE(_ID)`, `TOURNAMENT_WINNER_ROLE(_ID)`,
   `OWNER_ROLE_ID`, `SQL_DB_URI` and the rest. Any placeholder value works
   for those, e.g. `0` for an ID.

6. `docker compose up --build`. The SQLite database lives under `./database`
   and the log file under `./discord.log` on the host, both mounted into
   the container so they survive a restart.
7. Discord can take up to an hour to show newly registered slash commands
   to everyone the first time; that's Discord's own sync delay, not
   something this bot controls. Once they show up, run `/tour_create` in a
   `COMMAND_CHANNEL_IDS` channel as a `STAFF_ROLE_IDS` member.

## Develop it

```sh
python -m pip install -r requirements.txt
python -m pytest
```

Tests run without Discord or a real database: `tests/conftest.py` sets
placeholder settings, and the application-layer tests use an in-memory Unit
of Work.

## How it is organised

- `src/domains/tournament/{models,services,repositories,exceptions}.py` is
  the tournament feature that is actually wired to Discord: a plain
  dataclass, a service and a raw-SQL `aiosqlite` repository.
- `src/interfaces/discord/cogs/tournament_cog.py` and
  `src/infrastructure/discord/views/claim_code_view.py` hold the commands
  and the claim-code button.
- `src/domains/tournament/entities/`, `src/application/` and
  `src/infrastructure/persistence/sqlmodel/` are a richer, multi-phase
  tournament domain (SQLModel/SQLAlchemy, use cases, DTOs) from an
  in-progress rewrite. It's tested and runnable on its own
  (`src/main.py`), but it's not wired to the Discord commands yet, so the
  two live side by side for now.
- `tests/` covers both: the domain/application layer above, and (via
  `tests/conftest.py`) whatever needs the bot's settings to import cleanly.

## Since 2025

The tournament feature above, the part that ran on my server, is untouched.
In 2026 I moved the repository here, fixed the Docker entrypoint and the bot
startup (both were broken in every commit: the entrypoint pointed at a file
that didn't exist, and `bot.py` never actually called `bot.run()`), added CI
and semantic-release, and archived it.

## License

[MIT](LICENSE) © 2025 David Cohen
