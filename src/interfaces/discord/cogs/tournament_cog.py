from __future__ import annotations
from typing import Optional
from discord.ext import commands
from discord.ext.commands import Context, CommandError
from discord import app_commands
from src.application.tournament.tournament_service_old import TournamentService
from src.config.config import settings
from src.bot import DiscordBot
from src.infrastructure.discord.permissions import staff_only, command_channel_only, send_to_channel
from src.domains.tournament.repositories.exceptions import TournamentNotFound, TournamentInsertFailed
from src.domains.models import Tournament
from src.infrastructure.discord.views.claim_code_view import RequestCodeView
from src.infrastructure.persistence.sqllite.tournament_repository_old import SQLiteTournamentRepositoryOld
from src.utils.embeds import success_embed, info_embed, error_embed


class TournamentCog(commands.Cog):
    """Manage tournaments creation, update, listing, and deletion."""

    def __init__(self, bot: DiscordBot, service: TournamentService):
        self.bot = bot
        self.service = service
        self.config = settings

    async def cog_check(self, ctx: Context) -> bool:
        return await staff_only().predicate(ctx) and await command_channel_only().predicate(ctx)

    async def cog_command_error(self, ctx: Context, error: CommandError):
        """Gestione centralizzata errori per il cog Tournament."""

        if isinstance(error, commands.CommandInvokeError):
            error = error.original

        if isinstance(error, TournamentNotFound):
            await ctx.send(embed=error_embed("Not Found", str(error)))
            self.bot.logger.warning(f"Tournament not found: {error}")
            error.handled = True
            return
        elif isinstance(error, TournamentInsertFailed):
            await ctx.send(embed=error_embed("DB Error", "Could not save tournament. Try again."))
            self.bot.logger.exception(f"Insert failed: {error}")
            error.handled = True
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(embed=error_embed("Missing Argument", f"`{error.param.name.upper()}` is required."))
            error.handled = True
            return
        else:
            await ctx.send(embed=error_embed("Unexpected Error", str(error)))
            self.bot.logger.exception(f"Unhandled error: {type(error).__name__} - {error}")
            error.handled = True
            return


    from discord.ext import commands
    from discord.ext.commands import Context
    class Tournament(commands.Cog):
        def __init__(self, bot):
            self.bot = bot

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
        ctx,
        name: str,
        code: str,
        swiss: int,
        top_cut: int,
    ):
        tournament = await self.service.upsert(Tournament(
            server_id=ctx.guild.id,
            name=name,
            code=code,
            swiss=swiss,
            top_cut=top_cut,
        ))

        await ctx.send(embed=success_embed(
            title="Tournament Created",
            message=f"ID: `{tournament.id}`\n"
            f"Name: `{tournament.name}`\n"
            f"Code: `{tournament.code}`\n"
            f"Swiss Rounds: `{tournament.swiss}`\n"
            f"Top Cut: `{tournament.top_cut}`"
        ))

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
        tournament = await self.service.upsert(Tournament(
            id=tournament_id,
            server_id=ctx.guild.id,
            name=name,
            code=code,
            swiss=swiss,
            top_cut=top_cut,
        ))

        await ctx.send(embed=success_embed(
            title="Tournament Updated",
            message=f"ID: `{tournament.id}`\n"
            f"Name: `{tournament.name}`\n"
            f"Code: `{tournament.code}`\n"
            f"Swiss Rounds: `{tournament.swiss}`\n"
            f"Top Cut: `{tournament.top_cut}`"
        ))

    # ---------- DELETE ----------

    @commands.hybrid_command(name="tour_delete", description="Soft delete a tournament.")
    @app_commands.describe(tournament_id="Tournament ID to delete")
    async def delete_tour(
        self,
        ctx: Context,
        tournament_id: int,
        is_hard_delete: Optional[bool] = False
    ):
        if is_hard_delete:
            await self.service.delete(ctx.guild.id, tournament_id)
            await ctx.send(embed=success_embed(
                title="Tournament Hard Deleted",
                message=f"Tournament ID `{tournament_id}` removed.")
            )
        else:
            await self.service.soft_delete(ctx.guild.id, tournament_id)
            await ctx.send(embed=success_embed(
                title="Tournament Soft Deleted",
                message=f"Tournament ID `{tournament_id}` removed.")
            )

    # ---------- LIST ----------
    @commands.hybrid_command(name="tour_list", description="List all tournaments (optionally include deleted).")
    @app_commands.describe(show_deleted="Include tournaments that have been deleted.")
    async def get_all_tour(self, ctx: Context, show_deleted: bool = False):
        tournaments = await self.service.get_all(ctx.guild.id, include_deleted=show_deleted)

        if not tournaments:
            msg = "No tournaments are registered." if not show_deleted else "No tournaments found (even deleted)."
            await ctx.send(embed=info_embed(
                title="No Tournaments Found",
                message=msg))
            return

        lines = [
            f"{'❌' if t.is_deleted else '✅'} **{t.name}** (`{t.id}`) – Code: `{t.code or 'None'}`"
            for t in tournaments
        ]
        await ctx.send(embed=info_embed(
            title="Tournaments List",
            message="\n".join(lines))
        )

    # ---------- ANNOUNCE ----------

    @commands.hybrid_command(name="tour_announce", description="Send the tournament announcement.")
    @app_commands.describe(tournament_id="ID of the tournament to announce")
    async def send_tour_announce(self, ctx: Context, tournament_id: int):

        tournament = await self.service.get_by_id(ctx.guild.id, tournament_id)

        embed, view = RequestCodeView.create(
            service=self.service,
            tournament_id=tournament.id,
            tournament_name=tournament.name,
        )
        self.bot.add_view(view)

        await send_to_channel(
            ctx=ctx,
            guild=ctx.guild,
            bot=self.bot,
            embed=embed,
            view=view,
            channel_id=self.config.CODE_CHANNEL_ID
        )

        await ctx.send(
            embed=success_embed(
                title="Announcement Sent",
                message=f"Announced **{tournament.name}** (`{tournament.id}`)"),
            ephemeral=True
        )


async def setup(bot: DiscordBot):
    repo = SQLiteTournamentRepositoryOld(bot.connection)
    service = TournamentService(repo)
    await bot.add_cog(TournamentCog(bot, service))
