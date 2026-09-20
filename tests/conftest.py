"""Test-only environment defaults.

Settings are validated at import time (src/config/config.py), so importing
anything under ``src`` requires the environment below to be set. These are
placeholder values for the test run itself, not the bot's real configuration.
"""

import os

os.environ.setdefault("TOKEN", "test-token")
os.environ.setdefault("PREFIX", "!")
os.environ.setdefault("CODE_CHANNEL_ID", "1")
os.environ.setdefault("OWNER_ROLE", "Owner")
os.environ.setdefault("OWNER_ROLE_ID", "1")
os.environ.setdefault("RYUZEN_TEAM_ROLE", "Team")
os.environ.setdefault("RYUZEN_TEAM_ROLE_ID", "1")
os.environ.setdefault("TOURNAMENT_WINNER_ROLE", "Winner")
os.environ.setdefault("TOURNAMENT_WINNER_ROLE_ID", "1")
os.environ.setdefault("RR_MESSAGE_ID", "1")
os.environ.setdefault("SQL_DB_URI", "sqlite+aiosqlite:///:memory:")
