import discord
from discord.ext import commands
from discord.ext.commands import Context

from utils.roles import promote_member, demote_member
from utils.embeds import success_embed, error_embed
from utils.permissions import is_admin

async def resolve_member(guild: discord.Guild, user: discord.Member | discord.User, logger) -> discord.Member | None:
    """
    Garantisce che l'oggetto restituito sia un `discord.Member`, anche da `User` o ID.
    """
    if isinstance(user, discord.Member):
        logger.debug(f"[RoleManager] Resolved member directly: {user.display_name}")
        return user

    member = guild.get_member(user.id)
    if member:
        logger.debug(f"[RoleManager] Member found in cache: {member.display_name}")
        return member

    try:
        member = await guild.fetch_member(user.id)
        logger.debug(f"[RoleManager] Member fetched via API: {member.display_name}")
        return member
    except discord.NotFound:
        logger.warning(f"[RoleManager] Member with ID {user.id} not found.")
        return None


class RoleManager(commands.Cog, name="Role Manager"):
    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger

    @is_admin()
    @commands.hybrid_command(name="promote", description="Promote a user to the next role(s) in hierarchy.")
    async def promote(self, ctx: Context, user: discord.Member | discord.User):
        self.logger.debug(f"[RoleManager] Promotion requested for: {user}")
        member = await resolve_member(ctx.guild, user, self.logger)
        if not member:
            await ctx.send(embed=error_embed("User Not Found", f"Could not find `{user}` in this server."), ephemeral=True)
            return

        roles = await promote_member(ctx.guild, member)

        if roles:
            role_names = ", ".join(role.name for role in roles)
            self.logger.info(f"[RoleManager] {member.display_name} promoted to: {role_names}")
            await ctx.send(embed=success_embed("User Promoted", f"{member.mention} promoted to: **{role_names}**."), ephemeral=True)
        else:
            self.logger.info(f"[RoleManager] ❌ No promotable roles for {member.display_name}")
            await ctx.send(embed=error_embed("Promotion Failed", f"{member.mention} has no promotable roles."), ephemeral=True)

    @is_admin()
    @commands.hybrid_command(name="demote", description="Demote a user to the previous role(s) in hierarchy.")
    async def demote(self, ctx: Context, user: discord.Member | discord.User):
        self.logger.debug(f"[RoleManager] Demotion requested for: {user}")
        member = await resolve_member(ctx.guild, user, self.logger)
        if not member:
            await ctx.send(embed=error_embed("User Not Found", f"Could not find `{user}` in this server."), ephemeral=True)
            return

        roles = await demote_member(ctx.guild, member)

        if roles:
            role_names = ", ".join(role.name for role in roles)
            self.logger.info(f"[RoleManager] {member.display_name} demoted to: {role_names}")
            await ctx.send(embed=success_embed("User Demoted", f"{member.mention} demoted to: **{role_names}**."), ephemeral=True)
        else:
            self.logger.info(f"[RoleManager] ❌ No demotable roles for {member.display_name}")
            await ctx.send(embed=error_embed("Demotion Failed", f"{member.mention} has no demotable roles."), ephemeral=True)


async def setup(bot):
    await bot.add_cog(RoleManager(bot))
