from __future__ import annotations
from typing import Optional

from config import settings
from data.repositories.tournament_repository import TournamentRepository
from models.tournament_model import TournamentModel, TournamentInsertFailed, TournamentNotFound
from discord.ext import commands
from discord.ext.commands import Context
from discord import app_commands
from bot import DiscordBot
from services.tournament_service import TournamentService
from utils.embeds import success_embed, error_embed, info_embed
from utils.permissions import send_to_channel, staff_only, command_channel_only
from views.request_code_view import RequestCodeView


class Tournament(commands.Cog):
    """Manage tournaments creation, update, listing, and deletion."""

    def __init__(self, bot: DiscordBot, service: TournamentService):
        self.bot = bot
        self.service = service
        self.config = settings

    async def cog_check(self, ctx: Context) -> bool:
        return await staff_only().predicate(ctx) and await command_channel_only().predicate(ctx)

    # ---------- CREATE ----------
    @commands.hybrid_command(name="tour_create", description="Create a new tournament.")
    @app_commands.describe(
        name="Full name of the tournament",
        code="Access code",
        swiss="Number of Swiss rounds",
        top_cut="Top Cut size"
    )
    async def create_tour(
        self,
        ctx: Context,
        name: str,
        code: str,
        swiss: int,
        top_cut: int,
    ):
        try:
            tournament = await self.service.upsert(TournamentModel(
                server_id=ctx.guild.id,
                name=name,
                code=code,
                swiss=swiss,
                top_cut=top_cut,
            ))

            await ctx.send(embed=success_embed(
                "Tournament Created",
                f"ID: `{tournament.id}`\n"
                f"Name: `{tournament.name}`\n"
                f"Code: `{tournament.code}`\n"
                f"Swiss Rounds: `{tournament.swiss}`\n"
                f"Top Cut: `{tournament.top_cut}`"
            ))

        except TournamentInsertFailed:
            await ctx.send(embed=error_embed("DB Error", "Could not save tournament. Try again."))
            self.bot.logger.exception("Tournament creation failed.")
        except Exception as e:
            await ctx.send(embed=error_embed("Unexpected Error", str(e)))
            self.bot.logger.exception("Unhandled exception in create_tour")

    # ---------- UPDATE ----------
    @commands.hybrid_command(name="tour_update", description="Update an existing tournament.")
    @app_commands.describe(
        tournament_id="ID of the tournament to update",
        name="Updated name of the tournament",
        code="New access code",
        swiss="Updated number of Swiss rounds",
        top_cut="Updated Top Cut size"
    )
    async def update_tour(
        self,
        ctx: Context,
        tournament_id: int,
        name: str,
        code: str,
        swiss: Optional[int] = None,
        top_cut: Optional[int] = None,
    ):
        try:
            tournament = await self.service.upsert(TournamentModel(
                id=tournament_id,
                server_id=ctx.guild.id,
                name=name,
                code=code,
                swiss=swiss,
                top_cut=top_cut,
            ))

            await ctx.send(embed=success_embed(
                "Tournament Updated",
                f"ID: `{tournament.id}`\n"
                f"Name: `{tournament.name}`\n"
                f"Code: `{tournament.code}`\n"
                f"Swiss Rounds: `{tournament.swiss}`\n"
                f"Top Cut: `{tournament.top_cut}`"
            ))

        except TournamentNotFound:
            await ctx.send(embed=error_embed("Not Found", f"Tournament ID `{tournament_id}` not found."))
            self.bot.logger.warning(f"Tournament {tournament_id} not found in {ctx.guild.id}")
        except TournamentInsertFailed:
            await ctx.send(embed=error_embed("DB Error", "Could not update tournament. Try again."))
            self.bot.logger.exception("Tournament update failed.")
        except Exception as e:
            await ctx.send(embed=error_embed("Unexpected Error", str(e)))
            self.bot.logger.exception("Unhandled exception in update_tour")

    # ---------- GET ----------
    @commands.hybrid_command(name="code_get", description="Retrieve a stored tournament code.")
    @app_commands.describe(tournament_id="Tournament ID to retrieve the code for")
    async def get_code(self, ctx: Context, tournament_id: int):
        try:
            code = await self.service.get_code(ctx.guild.id, tournament_id)
            await ctx.send(embed=info_embed("Stored Code", f"`{code}`"))
        except TournamentNotFound:
            await ctx.send(embed=error_embed("No Code", f"`{tournament_id}` not found."))


    # ---------- DELETE ----------
    @commands.hybrid_command(name="tour_delete", description="Soft delete a tournament.")
    @app_commands.describe(tournament_id="Tournament ID to delete")
    async def delete_tour(
            self,
            ctx: Context,
            tournament_id: int,
            is_hard_delete: Optional[bool] = False):
        try:
            if is_hard_delete:
                await self.service.delete(ctx.guild.id, tournament_id)
                await ctx.send(embed=success_embed("Tournament Hard Deleted", f"Tournament ID `{tournament_id}` removed."))
                return
            else:
                await self.service.soft_delete(ctx.guild.id, tournament_id)
                await ctx.send(embed=success_embed("Tournament Soft Deleted", f"Tournament ID `{tournament_id}` removed."))
        except TournamentNotFound:
            await ctx.send(embed=error_embed("Not Found", f"Tournament ID `{tournament_id}` not found."))

    # ---------- LIST ----------
    @commands.hybrid_command(name="tour_list", description="List all tournaments (optionally include deleted).")
    @app_commands.describe(show_deleted="Include tournaments that have been deleted.")
    async def get_all_tour(self, ctx: Context, show_deleted: bool = False):
        tournaments = await self.service.get_all(ctx.guild.id, include_deleted=show_deleted)

        if not tournaments:
            title = "No Tournaments Found"
            msg = "No tournaments are registered." if not show_deleted else "No tournaments found (even deleted)."
            await ctx.send(embed=info_embed(title, msg))
            return

        lines = []
        for t in tournaments:
            deleted_mark = "❌ " if t.is_deleted else "✅"
            lines.append(f"{deleted_mark} **{t.name}** (`{t.id}`) – Code: `{t.code or 'None'}`")

        content = "\n".join(lines)

        await ctx.send(embed=info_embed(
            title="Tournaments List" + (" (with Deleted)" if show_deleted else ""),
            message=content
        ))

    @commands.hybrid_command(name="tour_announce",
                             description="Send the tournament announcement message to the code channel.")
    @app_commands.describe(tournament_id="ID of the tournament to announce")
    async def send_tour_announcement(self, ctx: Context, tournament_id: int):
        try:
            # Recupera il torneo dal DB
            tournaments = await self.service.get_all(ctx.guild.id)
            tournament = next((t for t in tournaments if t.id == tournament_id), None)

            if not tournament:
                await ctx.send(embed=error_embed("Not Found", f"Tournament ID `{tournament_id}` not found."),
                               ephemeral=True)
                return

            # Crea embed e pulsante
            embed, view = RequestCodeView.create(
                service=self.service,
                tournament_id=tournament.id,
                tournament_name=tournament.name,
            )
            self.bot.add_view(view)

            # Invia nel canale designato
            await send_to_channel(
                ctx=ctx,
                guild=ctx.guild,
                bot=self.bot,
                embed=embed,
                view=view,
                channel_id=self.config.CODE_CHANNEL_ID
            )

            await ctx.send(
                embed=success_embed("Announcement Sent", f"Announced **{tournament.name}** (`{tournament.id}`)"),
                ephemeral=True)

        except Exception as e:
            await ctx.send(embed=error_embed("Unexpected Error", str(e)), ephemeral=True)
            self.bot.logger.exception("Unhandled exception in send_tour_announcement")


async def setup(bot: DiscordBot):
    service = TournamentService(TournamentRepository(bot.database.connection))
    await bot.add_cog(Tournament(bot, service))
