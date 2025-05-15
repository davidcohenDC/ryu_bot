import os
from discord.ext import commands
from discord.ext.commands import Context
from discord import app_commands
from utils.embeds import success_embed, error_embed, warning_embed, info_embed
from utils.permissions import is_admin, is_allowed_channel, send_to_channel
from views.request_code_view import RequestCodeView

CODE_CHANNEL_ID = 1371542952257519626

class CodeManager(commands.Cog, name="Code Manager"):
    def __init__(self, bot):
        self.bot = bot

    @is_admin()
    @is_allowed_channel()
    @commands.hybrid_command(name="set_code", description="Set or update a code for a specific tournament.")
    @app_commands.describe(
        tournament_id="A unique ID for the tournament (e.g. celestial_guardians)",
        tournament_name="Full name of the tournament",
        new_code="Access code to assign"
    )
    async def set_code(self, ctx: Context, tournament_id: str, tournament_name: str, new_code: str):
        server_id = ctx.guild.id
        db = self.bot.database

        await db.set_code(server_id, tournament_id, new_code, tournament_name)

        await ctx.send(embed=success_embed(
            "Code Updated",
            f"🔐 Code: `{new_code}`\n🏆 Tournament: **{tournament_name}** (`{tournament_id}`)"
        ), ephemeral=True)

        embed, view = RequestCodeView.create(
            database=db,
            tournament_id=tournament_id,
            tournament_name=tournament_name
        )

        self.bot.add_view(view)  # rende la view persistente

        await send_to_channel(
            ctx,
            guild=ctx.guild,
            bot=self.bot,
            embed=embed,
            view=view,
            channel_id=CODE_CHANNEL_ID
        )

    @is_admin()
    @is_allowed_channel()
    @commands.hybrid_command(name="get_code", description="Retrieve a stored tournament code.")
    @app_commands.describe(tournament_id="Tournament ID to retrieve the code for")
    async def get_code(self, ctx: Context, tournament_id: str):
        code = await self.bot.database.get_code(ctx.guild.id, tournament_id)

        if code:
            await ctx.send(embed=info_embed("Stored Code", f"`{code}`"), ephemeral=True)
        else:
            await ctx.send(embed=error_embed("No Code Found", f"No code found for `{tournament_id}`."), ephemeral=True)

    @is_admin()
    @is_allowed_channel()
    @commands.hybrid_command(name="delete_code", description="Delete a tournament code.")
    @app_commands.describe(tournament_id="Tournament ID to delete the code for")
    async def delete_code(self, ctx: Context, tournament_id: str):
        server_id = ctx.guild.id
        db = self.bot.database
        code = await db.get_code(server_id, tournament_id)

        if not code:
            await ctx.send(embed=error_embed("No Code Found", f"No code found for `{tournament_id}`."), ephemeral=True)
            return

        await db.delete_code(server_id, tournament_id)
        await ctx.send(embed=success_embed("Code Deleted", f"Code for `{tournament_id}` has been removed."), ephemeral=True)

    @is_admin()
    @is_allowed_channel()
    @commands.hybrid_command(name="list_codes", description="List all active tournament codes.")
    async def list_codes(self, ctx: Context):
        server_id = ctx.guild.id
        db = self.bot.database
        tournaments = await db.list_codes(server_id)

        if not tournaments:
            await ctx.send(embed=info_embed("No Active Codes", "There are no codes currently stored."), ephemeral=True)
            return

        description = "\n".join([f"• **{name}** (`{tid}`)" for tid, name in tournaments])

        embed = info_embed(
            "Active Tournament Codes",
            description
        )
        await ctx.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(CodeManager(bot))
