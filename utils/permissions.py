from discord.ext import commands
from config import settings

def staff_only() -> commands.check:
    """Decoratore – consente l'uso solo ai ruoli in ``STAFF_ROLE_IDS``."""

    async def predicate(ctx: Context) -> bool:  # noqa: D401
        if ctx.author.id == ctx.bot.owner_id:
            return True
        for role in ctx.author.roles:
            if role.id in settings.STAFF_ROLE_IDS:
                return True
        raise MissingPermission()

    return commands.check(predicate)


def owner_only() -> commands.check:
    """Permette l’uso solo al proprietario dell’applicazione."""

    async def predicate(ctx: Context) -> bool:
        # is_owner() fa cache dopo la prima chiamata
        if await ctx.bot.is_owner(ctx.author):
            return True
        raise MissingPermission("You are not the bot owner.")

    return commands.check(predicate)


def command_channel_only() -> commands.check:
    """Decoratore – permette il comando solo nei canali di ``COMMAND_CHANNEL_IDS``."""

    async def predicate(ctx: Context) -> bool:  # noqa: D401
        if ctx.channel.id in settings.COMMAND_CHANNEL_IDS:
            return True
        raise WrongChannel()

    return commands.check(predicate)

class MissingPermission(commands.CheckFailure):
    def __init__(self, message="You don't have permission to use this command."):
        super().__init__(message)

class NotAMember(commands.CheckFailure):
    def __init__(self, message="You are not a member of this server."):
        super().__init__(message)

class WrongChannel(commands.CheckFailure):
    def __init__(self, message="This command cannot be used in this channel."):
        super().__init__(message)

import discord
from discord.ext.commands import Context

async def safe_send(
    ctx: Context,
    *,
    content: str | None = None,
    embed: discord.Embed | None = None,
    ephemeral: bool = True,
    followup_if_responded: bool = True
):
    """
    Safely sends a message:
    - Uses interaction.response.send_message() if available
    - Falls back to interaction.followup if already responded
    - Falls back to ctx.send() for prefixed commands
    """

    kwargs = {}
    if content:
        kwargs["content"] = content
    if embed:
        kwargs["embed"] = embed

    # Slash command mode
    if hasattr(ctx, "interaction") and ctx.interaction:
        interaction = ctx.interaction

        if not interaction.response.is_done():
            await interaction.response.send_message(**kwargs, ephemeral=ephemeral)
        elif followup_if_responded:
            await interaction.followup.send(**kwargs, ephemeral=ephemeral)
        else:
            raise RuntimeError("Interaction response already sent and followup disabled.")
    else:
        # Classic prefixed command fallback (ephemeral not supported)
        await ctx.send(**kwargs)

async def send_to_channel(
    ctx: Context,
    *,
    guild: discord.Guild,
    embed: discord.Embed,
    bot: discord.Client,
    view: discord.ui.View | None = None,
    channel_id: int | None = None,
    channel_name: str | None = None,
    confirm: bool = True,
    confirm_message: str = "Message successfully posted.",
    ephemeral: bool = True
) -> None:
    """
    Attempts to send an embed (and optional view) to a channel by name or ID.
    Raises WrongChannel if the channel is not found or accessible.
    Optionally sends a confirmation message to the current ctx.channel.
    """
    if channel_id:
        channel = guild.get_channel(channel_id)
    elif channel_name:
        channel = discord.utils.get(guild.text_channels, name=channel_name)
    else:
        raise WrongChannel("No channel ID or name provided.")

    if not channel:
        raise WrongChannel(f"Channel not found: {channel_name or channel_id}")

    try:
        await channel.send(embed=embed, view=view)

        if confirm:
            await ctx.send(confirm_message, ephemeral=ephemeral)

    except discord.Forbidden:
        raise WrongChannel(f"Missing permission to send messages to #{channel.name}.")
