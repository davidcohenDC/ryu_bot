from __future__ import annotations

"""
Centralised configuration loader.

Import ONE time at application start:

    from ryubot.config import settings
"""

import ast
import json
import os
from dataclasses import dataclass
from typing import Any, Callable, TypeVar

from dotenv import load_dotenv

load_dotenv()

T = TypeVar("T")


# ───────────────────────────────────────────────────────── helpers ────────────
def _parse_list(raw: str | None, cast: Callable[[str], T] = str) -> list[T]:
    """Convert an env-var to list[T].

    Handles:
        - "A,B,C"
        - '["A", "B"]'
        - "['A','B']"
    """
    if not raw:
        return []

    raw = raw.strip()
    if raw.startswith("["):
        try:
            data: list[Any] = json.loads(raw)
        except json.JSONDecodeError:
            data = ast.literal_eval(raw)
        return [cast(x) for x in data]

    return [cast(x.strip()) for x in raw.split(",") if x.strip()]


def _require(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _to_bool(raw: str | None, *, default: bool = False) -> bool:
    if raw is None:
        return default
    return raw.lower() in {"1", "true", "yes", "y", "on"}


# ───────────────────────────────────────────────────────── dataclass ───────────
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


# ──────────────────────────────────────────────────────── loader fn ────────────
def load_settings() -> Settings:
    """Read env-vars, cast/validate and return immutable Settings object."""
    return Settings(
        # --- core -----------------------------------------------------------
        TOKEN=_require("TOKEN"),
        PREFIX=_require("PREFIX"),
        INVITE_LINK=os.getenv("INVITE_LINK"),

        # --- permissions ----------------------------------------------------
        ALLOWED_CHANNELS=_parse_list(os.getenv("ALLOWED_CHANNELS")),
        ALLOWED_CHANNELS_ID=_parse_list(os.getenv("ALLOWED_CHANNELS_ID"), int),
        ALLOWED_ROLES=_parse_list(os.getenv("ALLOWED_ROLES")),
        ALLOWED_ROLES_ID=_parse_list(os.getenv("ALLOWED_ROLES_ID"), int),

        # --- code channels --------------------------------------------------
        CODE_CHANNEL_ID=int(_require("CODE_CHANNEL_ID")),
        CODE_GENERATION_CHANNEL=os.getenv("CODE_GENERATION_CHANNEL"),
        CODE_GENERATION_CHANNEL_ID=(
            int(os.getenv("CODE_GENERATION_CHANNEL_ID"))
            if os.getenv("CODE_GENERATION_CHANNEL_ID")
            else None
        ),

        # --- rule-reaction --------------------------------------------------
        RULE_REACTION_ID=(
            int(os.getenv("RULE_REACTION_ID"))
            if os.getenv("RULE_REACTION_ID")
            else None
        ),
        RULE_REACTION_TARGET_EMOJI=_parse_list(os.getenv("RULE_REACTION_TARGET_EMOJI")),

        # --- roles ----------------------------------------------------------
        OWNER_ROLE=_require("OWNER_ROLE"),
        OWNER_ROLE_ID=int(_require("OWNER_ROLE_ID")),
        RYUZEN_TEAM_ROLE=_require("RYUZEN_TEAM_ROLE"),
        RYUZEN_TEAM_ROLE_ID=int(_require("RYUZEN_TEAM_ROLE_ID")),
        TOURNAMENT_WINNER_ROLE=_require("TOURNAMENT_WINNER_ROLE"),
        TOURNAMENT_WINNER_ROLE_ID=int(_require("TOURNAMENT_WINNER_ROLE_ID")),

        # --- misc lists -----------------------------------------------------
        STAFF_ROLE_IDS=_parse_list(os.getenv("STAFF_ROLE_IDS"), int),
        COMMAND_CHANNEL_IDS=_parse_list(os.getenv("COMMAND_CHANNEL_IDS"), int),
        RR_MESSAGE_ID=int(_require("RR_MESSAGE_ID")),
        RR_EMOJI_NAMES=_parse_list(os.getenv("RR_EMOJI_NAMES")),

        # --- flags ----------------------------------------------------------
        DEBUG_REACTIONS=_to_bool(os.getenv("DEBUG_REACTIONS")),
    )


settings: Settings = load_settings()
