from __future__ import annotations

from discord import Member

from bot import DiscordBot

"""RoleManager – promuove / retrocede membri (owner‑only).

* I comandi sono disponibili **solo** all'owner del bot e solo nei canali
  definiti in ``COMMAND_CHANNEL_IDS``.
* La logica di permesso è centralizzata in ``cog_check``.
* Utilizza le utility ``promote_member`` e ``demote_member`` da
  :pymod:`utils.roles`.
"""

from typing import Final, Any, Coroutine

import discord
from discord.ext import commands
from discord.ext.commands import Context

from utils.roles import promote_member, demote_member
from utils.embeds import success_embed, error_embed
from utils.permissions import owner_only, command_channel_only


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

async def _resolve_member(guild: discord.Guild, user: discord.abc.User, logger) -> User | Member | None:
    """Garantisce che l'oggetto restituito sia un ``discord.Member``."""
    if isinstance(user, discord.Member):
        logger.debug("[RoleManager] Resolved member directly: %s", user.display_name)
        return user

    member = guild.get_member(user.id) or await guild.fetch_member(user.id)
    if member:
        logger.debug("[RoleManager] Member resolved: %s", member.display_name)
    else:
        logger.warning("[RoleManager] Member with ID %s not found.", user.id)
    return member


# ---------------------------------------------------------------------------
# Cog
# ---------------------------------------------------------------------------

class RoleManager(commands.Cog, name="Role Manager"):
    """Comandi di promozione / retrocessione ruoli."""

    CODE_EMOJI: Final = "⭐"  # esempio di costante declinabile

    def __init__(self, bot: DiscordBot):
        self.bot = bot
        self.logger = bot.logger

    # ─────────────────────────────  GLOBAL GUARD  ──────────────────────────
    async def cog_check(self, ctx: Context) -> bool:  # noqa: D401
        return await owner_only().predicate(ctx) and await command_channel_only().predicate(ctx)  # type: ignore[attr-defined]

    # ───────────────────────────────────────────────────────────────────────

    @commands.hybrid_command(name="promote", description="Promote a user to the next role(s) in hierarchy.")
    async def promote(self, ctx: Context, user: discord.Member | discord.User):
        member = await _resolve_member(ctx.guild, user, self.logger)
        if member is None:
            await ctx.send(embed=error_embed("User Not Found", f"Could not find `{user}` in this server."), ephemeral=True)
            return

        roles = await promote_member(ctx.guild, member)
        if roles:
            names = ", ".join(r.name for r in roles)
            await ctx.send(embed=success_embed("User Promoted", f"{member.mention} promoted to: **{names}**."), ephemeral=True)
            self.logger.info("[RoleManager] %s promoted to %s", member.display_name, names)
        else:
            await ctx.send(embed=error_embed("Promotion Failed", f"{member.mention} has no promotable roles."), ephemeral=True)
            self.logger.info("[RoleManager] No promotable roles for %s", member.display_name)

    # ───────────────────────────────────────────────────────────────────────

    @commands.hybrid_command(name="demote", description="Demote a user to the previous role(s) in hierarchy.")
    async def demote(self, ctx: Context, user: discord.Member | discord.User):
        member = await _resolve_member(ctx.guild, user, self.logger)
        if member is None:
            await ctx.send(embed=error_embed("User Not Found", f"Could not find `{user}` in this server."), ephemeral=True)
            return

        roles = await demote_member(ctx.guild, member)
        if roles:
            names = ", ".join(r.name for r in roles)
            await ctx.send(embed=success_embed("User Demoted", f"{member.mention} demoted to: **{names}**."), ephemeral=True)
            self.logger.info("[RoleManager] %s demoted to %s", member.display_name, names)
        else:
            await ctx.send(embed=error_embed("Demotion Failed", f"{member.mention} has no demotable roles."), ephemeral=True)
            self.logger.info("[RoleManager] No demotable roles for %s", member.display_name)


# ---------------------------------------------------------------------------
# Extension entrypoint
# ---------------------------------------------------------------------------

async def setup(bot: DiscordBot):
    await bot.add_cog(RoleManager(bot))
