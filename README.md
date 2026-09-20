# Ryu Bot

[![Build](https://github.com/davidcohenDC/ryu_bot/actions/workflows/build.yml/badge.svg)](https://github.com/davidcohenDC/ryu_bot/actions/workflows/build.yml)
[![Release](https://img.shields.io/github/v/release/davidcohenDC/ryu_bot)](https://github.com/davidcohenDC/ryu_bot/releases/latest)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A Discord bot I wrote to run tournaments on my own server: create them,
update them, list them, delete them, and post an announcement with a button
people click to get their entry code by DM.

Parked here as-is for now.

## What it does

- `/tour_create`, `/tour_update`, `/tour_delete`, `/tour_list`,
  `/tour_announce`: one Swiss + Top Cut tournament per server.
- Only staff can use them, and only in specific channels
  (`STAFF_ROLE_IDS`, `COMMAND_CHANNEL_IDS`).
- The announcement has a "Claim Code" button. Click it and you get your
  code by DM. Heads up: if the bot restarts, the button stops working until
  someone runs `/tour_announce` again.
- There's also some reaction-role code lying around
  (`src/utils/reactions.py`, `src/utils/roles.py`), but nothing calls it, so
  it doesn't actually do anything right now.

## Getting it running for real

`docker compose up` gets the process running, but making it actually talk
to your server takes a few steps first:

1. Create an app and a bot at the
   [Discord Developer Portal](https://discord.com/developers/applications),
   grab the token.
2. On the Bot page, turn on the three privileged intents: Message Content,
   Server Members, Presence. The bot asks for all three, and Discord won't
   let it connect otherwise.
3. Generate an invite link (OAuth2 > URL Generator), scopes `bot` and
   `applications.commands`, permissions at least Send Messages, Embed Links
   and Read Message History. Invite it to your server.
4. Turn on Developer Mode in Discord (User Settings > Advanced) so you can
   right-click and copy role/channel IDs.
5. Clone the repo, copy `.env.example` to `.env`, and fill in:

   ```sh
   git clone https://github.com/davidcohenDC/ryu_bot.git
   cd ryu_bot
   cp .env.example .env
   ```

   - `TOKEN`: from step 1
   - `PREFIX`: whatever you want, e.g. `!`
   - `STAFF_ROLE_IDS`: who can run the commands
   - `COMMAND_CHANNEL_IDS`: where they can run them
   - `CODE_CHANNEL_ID`: where the announcement goes

   Everything else in `.env.example` just needs some value to satisfy the
   settings check on startup, it's not actually read anywhere yet.

6. `docker compose up --build`. The database and log file are mounted from
   the host, so they survive a restart.
7. The first time, Discord can take up to an hour to show the new slash
   commands everywhere. Once they show up, try `/tour_create`.

## Developing it

```sh
pip install -r requirements.txt
pytest
```

Tests don't need Discord or a real database, `conftest.py` fakes the
settings.

## Layout

- `src/domains/tournament/{models,services,repositories,exceptions}.py` is
  the part actually wired to Discord.
- `src/interfaces/discord/cogs/tournament_cog.py` and
  `src/infrastructure/discord/views/claim_code_view.py` are the commands
  and the button.
- `src/domains/tournament/entities/`, `src/application/` and
  `src/infrastructure/persistence/sqlmodel/` are a bigger rewrite in
  progress (multi-phase tournaments). Tested, but not hooked up to Discord
  yet.
- `tests/` covers both.

## License

MIT (see [LICENSE](LICENSE)) © 2025 David Cohen
