from __future__ import annotations

import emoji
import discord
from discord.ext import commands
from bot import DiscordBot
from config import settings
from utils.roles import promote_member, demote_member


# ────────────────────────── costanti di configurazione
TARGET_MESSAGE_ID: int                 = settings.RR_MESSAGE_ID          # ex TARGET_MESSAGE_ID
TARGET_EMOJI_NAMES: list[str]          = settings.RR_EMOJI_NAMES         # ex TARGET_EMOJI_NAMES
VERBOSE: bool                          = settings.DEBUG_REACTIONS        # log extra facoltativo

TARGET_EMOJI_CHARS = {emoji.emojize(e, language="alias") for e in TARGET_EMOJI_NAMES}


# ────────────────────────── helper “puri” (facili da testare)
def is_target_reaction(payload: discord.RawReactionActionEvent) -> bool:
    """True se la reaction corrisponde al messaggio/emoji configurati."""
    return (
        payload.message_id == TARGET_MESSAGE_ID
        and payload.emoji.name in TARGET_EMOJI_CHARS
    )


async def fetch_member(guild: discord.Guild, user_id: int) -> discord.Member | None:
    """Garantisce un `discord.Member` da cache o API; None se non trovato."""
    return guild.get_member(user_id) or await guild.fetch_member(user_id)


async def temp_reply(
    message: discord.Message,
    member: discord.Member,
    text: str,
    *,
    timeout: int = 10,
) -> None:
    """Risponde al messaggio e autodelete dopo `timeout` secondi."""
    await message.reply(
        f"{member.mention} {text}",
        delete_after=timeout,
        mention_author=False,
    )


# ────────────────────────── Cog principale
class ReactionRole(commands.Cog, name="Reaction Role"):
    """Aggiunge/Revoca ruoli quando l’utente mette/toglie la reaction giusta."""

    def __init__(self, bot: DiscordBot):
        self.bot = bot
        self.log = bot.logger

    # ---------- core ----------
    async def _handle(self, payload: discord.RawReactionActionEvent, *, promote: bool):
        if not is_target_reaction(payload):
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:  # guild could be None if bot left meanwhile
            return

        member = await fetch_member(guild, payload.user_id)
        if not member or member.bot:
            return

        roles = (
            await promote_member(guild, member)
            if promote
            else await demote_member(guild, member)
        )
        if not roles:
            if VERBOSE:
                self.log.info(
                    "[ReactionRole] No roles to %s for %s",
                    "promote" if promote else "demote",
                    member.display_name,
                )
            return

        names = ", ".join(r.name for r in roles)
        action = "promoted" if promote else "demoted"
        self.log.info("[ReactionRole] %s %s → %s", member.display_name, action, names)

        # feedback rapido nell’UI
        channel = guild.get_channel(payload.channel_id)
        if channel:
            try:
                msg = await channel.fetch_message(payload.message_id)
                verb = "verified" if promote else "revoked"
                await temp_reply(msg, member, f"your verification was **{verb}**: `{names}`")
            except (discord.Forbidden, discord.NotFound):
                pass  # niente panico se il bot non può leggere quel messaggio

    # ---------- listeners ----------
    @commands.Cog.listener("on_raw_reaction_add")
    async def _on_add(self, p: discord.RawReactionActionEvent):
        if VERBOSE:
            self.log.debug("[ReactionRole] reaction add by %s", p.user_id)
        await self._handle(p, promote=True)

    @commands.Cog.listener("on_raw_reaction_remove")
    async def _on_remove(self, p: discord.RawReactionActionEvent):
        if VERBOSE:
            self.log.debug("[ReactionRole] reaction remove by %s", p.user_id)
        await self._handle(p, promote=False)


# ────────────────────────── setup entry-point
async def setup(bot: DiscordBot):
    await bot.add_cog(ReactionRole(bot))
