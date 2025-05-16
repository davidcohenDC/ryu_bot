from __future__ import annotations

"""Centralised configuration loader.

Import *once* at application start::

    from settings import settings

All variables are validated / converted to the correct type so the rest of the
code never deals with raw strings from the environment.
"""

import os
import json
import ast
from dataclasses import dataclass
from typing import Any, Callable, TypeVar, Generic

from dotenv import load_dotenv

# Ensure .env is loaded before we access os.getenv
load_dotenv()

T = TypeVar("T")


def _parse_list(raw: str, cast: Callable[[str], T] = str) -> list[T]:
    """Parse an env-var representing a list.

    Handles formats like::

        BOT,GENERAL
        ["bot", "general"]
        ['bot', 'general']

    ``cast`` decides the final element type (``str`` by default, ``int`` for
    numeric IDs, ecc.).
    """
    raw = raw.strip()
    if not raw:
        return []

    if raw.startswith("["):
        try:
            data: list[Any] = json.loads(raw)
        except json.JSONDecodeError:
            # Fallback: Python literal list/tuple
            data = ast.literal_eval(raw)
        return [cast(x) for x in data]

    # Comma‑separated string
    return [cast(x.strip()) for x in raw.split(",") if x.strip()]


@dataclass(slots=True, frozen=True)
class Settings:
    TOKEN: str
    PREFIX: str
    INVITE_LINK: str | None

    ALLOWED_CHANNELS: list[str]
    ALLOWED_CHANNELS_ID: list[int]
    ALLOWED_ROLES: list[str]
    ALLOWED_ROLES_ID: list[int]

    CODE_CHANNEL_ID: int
    CODE_GENERATION_CHANNEL: str | None
    CODE_GENERATION_CHANNEL_ID: int | None

    RULE_REACTION_ID: int | None
    RULE_REACTION_TARGET_EMOJI: list[str]

    OWNER_ROLE: str
    OWNER_ROLE_ID: int
    RYUZEN_TEAM_ROLE: str
    RYUZEN_TEAM_ROLE_ID: int
    TOURNAMENT_WINNER_ROLE: str
    TOURNAMENT_WINNER_ROLE_ID: int
    STAFF_ROLE_IDS: list[int]
    COMMAND_CHANNEL_IDS: list[int]
    RR_MESSAGE_ID: int
    RR_EMOJI_NAMES: list[str]
    DEBUG_REACTIONS: bool


# ────────────────────────────────────────────────────────────────────────────
# Loader
# ────────────────────────────────────────────────────────────────────────────

def _require(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def load_settings() -> Settings:
    return Settings(
        TOKEN=_require("TOKEN"),
        PREFIX=_require("PREFIX"),
        INVITE_LINK=os.getenv("INVITE_LINK"),
        STAFF_ROLE_IDS = _parse_list(os.getenv("STAFF_ROLE_IDS", ""), int),
        COMMAND_CHANNEL_IDS = _parse_list(os.getenv("COMMAND_CHANNEL_IDS", ""), int),
        ALLOWED_CHANNELS=_parse_list(os.getenv("ALLOWED_CHANNELS", ""), str),
        ALLOWED_CHANNELS_ID=_parse_list(os.getenv("ALLOWED_CHANNELS_ID", ""), int),
        ALLOWED_ROLES=_parse_list(os.getenv("ALLOWED_ROLES", ""), str),
        ALLOWED_ROLES_ID=_parse_list(os.getenv("ALLOWED_ROLES_ID", ""), int),

        CODE_CHANNEL_ID=int(_require("CODE_CHANNEL_ID")),
        CODE_GENERATION_CHANNEL=os.getenv("CODE_GENERATION_CHANNEL"),
        CODE_GENERATION_CHANNEL_ID=os.getenv("CODE_GENERATION_CHANNEL_ID") and int(os.getenv("CODE_GENERATION_CHANNEL_ID")),

        RULE_REACTION_ID=os.getenv("RULE_REACTION_ID") and int(os.getenv("RULE_REACTION_ID")),
        RULE_REACTION_TARGET_EMOJI=_parse_list(os.getenv("RULE_REACTION_TARGET_EMOJI", ""), str),

        OWNER_ROLE=_require("OWNER_ROLE"),
        OWNER_ROLE_ID=int(_require("OWNER_ROLE_ID")),
        RYUZEN_TEAM_ROLE=_require("RYUZEN_TEAM_ROLE"),
        RYUZEN_TEAM_ROLE_ID=int(_require("RYUZEN_TEAM_ROLE_ID")),
        TOURNAMENT_WINNER_ROLE=_require("TOURNAMENT_WINNER_ROLE"),
        TOURNAMENT_WINNER_ROLE_ID=int(_require("TOURNAMENT_WINNER_ROLE_ID")),
        RR_MESSAGE_ID=int(_require("RR_MESSAGE_ID")),
        RR_EMOJI_NAMES=_parse_list(os.getenv("RR_EMOJI_NAMES", ""), str),
        # get boolean value from env var, default to False
        DEBUG_REACTIONS=bool(os.getenv("DEBUG_REACTIONS", "False"),
    ))


settings: Settings = load_settings()
