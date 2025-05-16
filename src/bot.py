import logging
import os
import pathlib
import platform
import aiosqlite
import discord
from discord.ext import commands
from discord.ext.commands import Context
from dotenv import load_dotenv
from config import settings
from core.logger import LoggingFormatter
from src.infrastructure.discord.permissions import WrongChannel, MissingPermission
from src.utils.embeds import error_embed

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
intents.members = True  # THIS is the key line
intents.guilds = True
intents.reactions = True

logger = logging.getLogger("discord_bot")
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(LoggingFormatter())
# File handler
file_handler = logging.FileHandler(filename="../discord.log", encoding="utf-8", mode="w")
file_handler_formatter = logging.Formatter(
    "[{asctime}] [{levelname:<8}] {name}: {message}", "%Y-%m-%d %H:%M:%S", style="{"
)
file_handler.setFormatter(file_handler_formatter)

# Add the handlers
logger.addHandler(console_handler)
logger.addHandler(file_handler)

class DiscordBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix=commands.when_mentioned_or(settings.PREFIX),
            intents=intents,
            help_command=None,
        )

        self.logger = logger
        self.connection = None
        self.settings = settings
        self.bot_prefix = self.settings.PREFIX
        self.invite_link = self.settings.INVITE_LINK

    async def init_db(self) -> None:
        async with aiosqlite.connect("src/database/database.db") as db:
            with open("src/database/schema.sql", encoding="utf-8") as file:
                await db.executescript(file.read())
            await db.commit()

    async def load_cogs(self) -> None:
        cogs_dir = pathlib.Path("src/interfaces/discord/cogs")
        for path in cogs_dir.rglob("*.py"):
            if path.name.startswith("_"):
                continue  # skip __init__.py or private files

            relative_path = path.with_suffix("")  # remove .py
            module_path = ".".join(relative_path.parts)  # es: cogs.tournament.code_manager

            try:
                await self.load_extension(module_path)
                self.logger.info(f"Loaded extension '{module_path}'")
            except Exception as e:
                self.logger.error(f"Failed to load extension {module_path}\n{type(e).__name__}: {e}")


    async def setup_hook(self) -> None:
        self.logger.info(f"Logged in as {self.user.name}")
        self.logger.info(f"discord.py API version: {discord.__version__}")
        self.logger.info(f"Python version: {platform.python_version()}")
        self.logger.info(f"Running on: {platform.system()} {platform.release()} ({os.name})")
        self.logger.info("-------------------")
        # connessione al DB

        db_path = os.path.join(os.path.dirname(__file__), "database", "database.db")
        self.connection = await aiosqlite.connect(db_path)

        await self.init_db()
        await self.load_cogs()
        self.logger.info("Bot commands: %s",
                         [cmd.name for cmd in self.commands])

        synced = await self.tree.sync()
        self.logger.info(f"✅ Slash commands sincronizzati: {len(synced)} comandi registrati.")



    async def on_message(self, message: discord.Message) -> None:
        """
        The code in this event is executed every time someone sends a message, with or without the prefix

        :param message: The message that was sent.
        """
        if message.author == self.user or message.author.bot:
            return
        await self.process_commands(message)

    async def on_command_completion(self, context: Context) -> None:
        """
        The code in this event is executed every time a normal command has been *successfully* executed.

        :param context: The context of the command that has been executed.
        """
        full_command_name = context.command.qualified_name
        split = full_command_name.split(" ")
        executed_command = str(split[0])
        if context.guild is not None:
            self.logger.info(
                f"Executed {executed_command} command in {context.guild.name} (ID: {context.guild.id}) by {context.author} (ID: {context.author.id})"
            )
        else:
            self.logger.info(
                f"Executed {executed_command} command by {context.author} (ID: {context.author.id}) in DMs"
            )

    async def on_command_error(self, context: Context, error) -> None:
        """
        This event is triggered whenever a valid command runs into an error.

        :param context: The context of the command that failed.
        :param error: The error that occurred.
        """
        if isinstance(error, commands.CommandOnCooldown):
            minutes, seconds = divmod(error.retry_after, 60)
            hours, minutes = divmod(minutes, 60)
            hours = hours % 24
            time_parts = []
            if round(hours) > 0:
                time_parts.append(f"{round(hours)} hours")
            if round(minutes) > 0:
                time_parts.append(f"{round(minutes)} minutes")
            if round(seconds) > 0:
                time_parts.append(f"{round(seconds)} seconds")

            embed = error_embed(
                title="*Sniff sniff!*",
                message="You're going too fast! Let me rest my wings... Try again in "
                        + " ".join(time_parts) + "."
            )
            await context.send(embed=embed)

        elif isinstance(error, commands.NotOwner):
            embed = error_embed(
                title="Gasp!",
                message="Only my master can use this command! And you... you’re not them!"
            )
            await context.send(embed=embed)
            if context.guild:
                self.logger.warning(
                    f"{context.author} (ID: {context.author.id}) tried to execute an owner only command in the guild {context.guild.name} (ID: {context.guild.id}), but the user is not an owner of the bot."
                )
            else:
                self.logger.warning(
                    f"{context.author} (ID: {context.author.id}) tried to execute an owner only command in the bot's DMs, but the user is not an owner of the bot."
                )

        elif isinstance(error, commands.MissingPermissions):
            embed = error_embed(
                title="Uh-oh!",
                message="You need the following shiny permissions to do that: `"
                            + ", ".join(error.missing_permissions)
                            + "`! Without them, my magic won’t work!"
            )
            await context.send(embed=embed)

        elif isinstance(error, commands.BotMissingPermissions):
            embed = error_embed(
                title="Oopsie!",
                message="Oopsie! I can't complete that because I'm missing: `"
                            + ", ".join(error.missing_permissions)
                            + "`! Can you help me get those?"
            )
            await context.send(embed=embed)

        elif isinstance(error, MissingPermission):
            self.logger.warning(
                f"{context.author} tried to use `{context.command}` but it’s not allowed."
            )
            await context.send(
                embed=error_embed(
                    title="Nuh-uh!",
                    message=f"Only the mighty **{settings.OWNER_ROLE}** role can use this command. That’s the rule!"
                ))

        elif isinstance(error, WrongChannel):
            self.logger.warning(
                f"{context.author} tried to use `{context.command}` in #{context.channel.name} but it’s not allowed."
            )
            await context.send(
                embed=error_embed(
                    title="Wrong Spot!",
                    message=f"You can't cast that here! Use this command in: {', '.join(f'<#{cid}>' for cid in settings.COMMAND_CHANNEL_IDS)}"
                ))
