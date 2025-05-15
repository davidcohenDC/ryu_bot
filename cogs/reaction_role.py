import os
import emoji
import discord
from discord.ext import commands

from utils.roles import promote_member, demote_member

# === CONFIGURATION ===
TARGET_MESSAGE_ID = int(os.getenv("TARGET_MESSAGE_ID", "1371600446531305605"))
TARGET_EMOJI_NAMES = [":heart:", ":hearts:"]

def is_target_reaction(payload: discord.RawReactionActionEvent) -> bool:
    emoji_chars = [emoji.emojize(e, language="alias") for e in TARGET_EMOJI_NAMES]
    return payload.message_id == TARGET_MESSAGE_ID and payload.emoji.name in emoji_chars

async def get_member(guild: discord.Guild, user_id: int, logger) -> discord.Member | None:
    member = guild.get_member(user_id)
    if member:
        return member
    try:
        member = await guild.fetch_member(user_id)
        logger.debug(f"[ReactionRole] Member fetched via API: {member.display_name}")
        return member
    except discord.NotFound:
        logger.warning(f"[ReactionRole] Member with ID {user_id} not found.")
        return None

async def send_temp_reply(channel, message_id, member, text: str, logger):
    try:
        message = await channel.fetch_message(message_id)
        await message.reply(
            content=f"{member.mention} {text}",
            delete_after=10,
            mention_author=False
        )
    except Exception as e:
        logger.error(f"[ReactionRole] ❗ Could not send confirmation: {e}")

class ReactionRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger

    async def handle_roles(self, payload: discord.RawReactionActionEvent, promote: bool):
        if not is_target_reaction(payload):
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        member = await get_member(guild, payload.user_id, self.logger)
        if not member or member.bot:
            return

        roles = await promote_member(guild, member) if promote else await demote_member(guild, member)

        if not roles:
            self.logger.info(f"[ReactionRole] No roles to {'promote' if promote else 'revoke'} for {member.display_name}")
            return

        changed_names = ", ".join(role.name for role in roles)
        action = "promoted" if promote else "demoted"
        self.logger.info(f"[ReactionRole] {member.display_name} {action} → {changed_names}")

        channel = guild.get_channel(payload.channel_id)
        if channel:
            verb = "verified" if promote else "revoked"
            await send_temp_reply(channel, payload.message_id, member, f"your verification was {verb}: `{changed_names}`", self.logger)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        self.logger.debug(f"[ReactionRole] ✅ Reaction added by user ID {payload.user_id}")
        await self.handle_roles(payload, promote=True)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        self.logger.debug(f"[ReactionRole] ❌ Reaction removed by user ID {payload.user_id}")
        await self.handle_roles(payload, promote=False)

async def setup(bot):
    await bot.add_cog(ReactionRole(bot))
