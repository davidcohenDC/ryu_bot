from __future__ import annotations

from models.tournament import Tournament   # e non più dal cog
from discord.ext import commands
from discord.ext.commands import Context
from discord import app_commands
from bot import DiscordBot
from services.codes import CodeService
from utils.embeds import success_embed, error_embed, info_embed
from utils.permissions import send_to_channel, staff_only, command_channel_only
from views.request_code_view import RequestCodeView

class CodeManager(commands.Cog, name="Code Manager"):
    """CRUD Tournament Codes."""

    def __init__(self, bot: DiscordBot, codes: CodeService):
        self.bot = bot
        self.codes = codes        # dipendenza iniettata
        self.settings = bot.settings

    # ─────────────────────────────  GLOBAL GUARD  ──────────────────────────
    async def cog_check(self, ctx: Context) -> bool:  # noqa: D401
        return await staff_only().predicate(ctx) and await command_channel_only().predicate(ctx)

    # ---------- CREATE / UPDATE ----------
    @commands.hybrid_command(name="set_code", description="Add or update the code of a tournament.")
    @app_commands.describe(
        tournament_id="Unique ID for the tournament",
        tournament_name="Full name of the tournament",
        new_code="Access code to assign",
    )
    async def set_code(
        self,
        ctx: Context,
        tournament_id: str,
        tournament_name: str,
        new_code: str,
    ):
        t = Tournament(tournament_id, tournament_name, new_code)

        await self.codes.upsert(ctx.guild.id, t)

        await ctx.send(
            embed=success_embed("Code Updated", f"🔐 `{t.code}` – **{t.name}** (`{t.id}`)"),
            ephemeral=True,
        )

        # La view ha ancora bisogno del DB grezzo → lo otteniamo dal service
        embed, view = RequestCodeView.create(
            database=self.codes.repo,  # type: ignore[attr-defined]
            tournament_id=t.id,
            tournament_name=t.name,
        )
        self.bot.add_view(view)

        await send_to_channel(
            ctx,
            guild=ctx.guild,
            bot=self.bot,
            embed=embed,
            view=view,
            channel_id=self.settings.CODE_CHANNEL_ID,
        )

    # ---------- READ ----------
    @commands.hybrid_command(name="get_code", description="Retrieve a stored tournament code.")
    @app_commands.describe(tournament_id="Tournament ID to retrieve the code for")
    async def get_code(self, ctx: Context, tournament_id: str):
        code = await self.codes.fetch(ctx.guild.id, tournament_id)

        if code:
            await ctx.send(embed=info_embed("Stored Code", f"`{code}`"), ephemeral=True)
        else:
            await ctx.send(
                embed=error_embed("No Code", f"`{tournament_id}` non trovato."),
                ephemeral=True,
            )

    # ---------- DELETE ----------
    @commands.hybrid_command(name="delete_code", description="Delete a tournament code.")
    @app_commands.describe(tournament_id="Tournament ID to delete the code for")
    async def delete_code(self, ctx: Context, tournament_id: str):
        if not await self.codes.fetch(ctx.guild.id, tournament_id):
            await ctx.send(
                embed=error_embed("No Code", f"`{tournament_id}` non trovato."),
                ephemeral=True,
            )
            return

        await self.codes.remove(ctx.guild.id, tournament_id)
        await ctx.send(embed=success_embed("Code Deleted", f"`{tournament_id}` rimosso."), ephemeral=True)

    # ---------- LIST ----------
    @commands.hybrid_command(name="list_codes", description="List all active tournament codes.")
    async def list_codes(self, ctx: Context):

        rows = await self.codes.list(ctx.guild.id)

        if not rows:
            await ctx.send(embed=info_embed("No Active Codes", "Nessun codice registrato."), ephemeral=True)
            return

        lines = "\n".join(f"• **{name}** (`{tid}`)" for tid, name in rows)
        await ctx.send(embed=info_embed("Active Tournament Codes", lines), ephemeral=True)


async def setup(bot: DiscordBot):
    codes = CodeService(bot.database)
    await bot.add_cog(CodeManager(bot, codes))
