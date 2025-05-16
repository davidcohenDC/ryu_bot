import discord

EMBED_COLOR_SUCCESS = 0x57F287
EMBED_COLOR_ERROR = 0xE02B2B
EMBED_COLOR_INFO = 0x5865F2

def create_embed(title: str, description: str, color: int) -> discord.Embed:
    return discord.Embed(title=title, description=description, color=color)

def error_embed(title: str, message: str) -> discord.Embed:
    return discord.Embed(
        title=f":x: {title}",
        description=message,
        color=EMBED_COLOR_ERROR,
    )

def success_embed(title: str, message: str) -> discord.Embed:
    return discord.Embed(
        title=f":white_check_mark: {title}",
        description=message,
        color=EMBED_COLOR_SUCCESS,
    )

def info_embed(title: str, message: str) -> discord.Embed:
    return discord.Embed(
        title=f":information_source: {title}",
        description=message,
        color=EMBED_COLOR_INFO,
    )

def warning_embed(title: str, message: str) -> discord.Embed:
    return discord.Embed(
        title=f":warning: {title}",
        description=message,
        color=0xFFA500,  # Orange color for warning
    )