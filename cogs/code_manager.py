import os
from discord.ext import commands
from discord.ext.commands import Context
from utils.embeds import success_embed, error_embed, warning_embed, info_embed
from utils.permissions import is_admin, is_allowed_channel, send_to_channel
from views.request_code_view import RequestCodeView

CODE_CHANNEL_ID = 1371542952257519626

class CodeManager(commands.Cog, name="Code Manager"):
    def __init__(self, bot):
        self.bot = bot

    @is_admin()
    @is_allowed_channel()
    @commands.hybrid_command(name="set_code", description="Set or update a server-wide code and post the request button.")
    async def set_code(self, ctx: Context, *, new_code: str = None):

        server_id = ctx.guild.id
        db = self.bot.database
        current_code = await db.get_code(server_id)

        if current_code and not new_code:
            await ctx.send(
                embed=warning_embed("Code Already Exists", f"Use {os.getenv('PREFIX')}generate_code <new_code> to overwrite it."),
                ephemeral=True
            )
            return

        if new_code:
            await db.set_code(server_id, new_code)
            await ctx.send(embed=success_embed("Code Updated", f"The code is now: {new_code}"), ephemeral=True)
        elif not current_code:
            await ctx.send(embed=error_embed("No Code Set", "Please provide a code."), ephemeral=True)
            return

        embed_request, view = RequestCodeView.create(database=db, server_id=ctx.guild.id)

        await send_to_channel(
            ctx,
            guild=ctx.guild,
            bot=self.bot,
            embed=embed_request,
            view=view,
            channel_id=CODE_CHANNEL_ID
        )

    @is_admin()
    @is_allowed_channel()
    @commands.hybrid_command(name="get_code", description="Retrieve the currently stored code.")
    async def get_code(self, ctx: Context):
        code = await self.bot.database.get_code(ctx.guild.id)

        if code:
            await ctx.send(embed=info_embed("Stored Code", f"{code}"), ephemeral=True)
        else:
            await ctx.send(embed=error_embed("No Code Set", "No code found."), ephemeral=True)

    @is_admin()
    @is_allowed_channel()
    @commands.hybrid_command(name="delete_code", description="Delete the currently stored code.")
    async def delete_code(self, ctx: Context):
        server_id = ctx.guild.id
        db = self.bot.database
        current_code = await db.get_code(server_id)

        if not current_code:
            await ctx.send(embed=error_embed("No Code Set", "No code found."), ephemeral=True)
            return

        await db.delete_code(server_id)
        await ctx.send(embed=success_embed("Code Deleted", "The code has been deleted."), ephemeral=True)

async def setup(bot):
    await bot.add_cog(CodeManager(bot))