import logging
import os
import platform
from config import settings
import aiosqlite
import discord

from discord.ext import commands, tasks
from discord.ext.commands import Context
from dotenv import load_dotenv

from utils.embeds import error_embed
from utils.permissions import MissingPermission, WrongChannel
from database import DatabaseManager

load_dotenv()

"""	
Setup bot intents (events restrictions)
For more information about intents, please go to the following websites:
https://discordpy.readthedocs.io/en/latest/intents.html
https://discordpy.readthedocs.io/en/latest/intents.html#privileged-intents


Default Intents:
intents.bans = True
intents.dm_messages = True
intents.dm_reactions = True
intents.dm_typing = True
intents.emojis = True
intents.emojis_and_stickers = True
intents.guild_messages = True
intents.guild_reactions = True
intents.guild_scheduled_events = True
intents.guild_typing = True
intents.guilds = True
intents.integrations = True
intents.invites = True
intents.messages = True # `message_content` is required to get the content of the messages
intents.reactions = True
intents.typing = True
intents.voice_states = True
intents.webhooks = True

Privileged Intents (Needs to be enabled on developer portal of Discord), please use them only if you need them:
intents.members = True
intents.message_content = True
intents.presences = True
"""

intents = discord.Intents.default()

"""
Uncomment this if you want to use prefix (normal) commands.
It is recommended to use slash commands and therefore not use prefix commands.

If you want to use prefix commands, make sure to also enable the intent below in the Discord developer portal.
"""
intents.message_content = True
intents.presences = True
intents.members = True  # THIS is the key line
intents.guilds = True
intents.reactions = True
# Setup both of the loggers


class LoggingFormatter(logging.Formatter):
    # Colors
    black = "\x1b[30m"
    red = "\x1b[31m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    blue = "\x1b[34m"
    gray = "\x1b[38m"
    # Styles
    reset = "\x1b[0m"
    bold = "\x1b[1m"

    COLORS = {
        logging.DEBUG: gray + bold,
        logging.INFO: blue + bold,
        logging.WARNING: yellow + bold,
        logging.ERROR: red,
        logging.CRITICAL: red + bold,
    }

    def format(self, record):
        log_color = self.COLORS[record.levelno]
        format = "(black){asctime}(reset) (levelcolor){levelname:<8}(reset) (green){name}(reset) {message}"
        format = format.replace("(black)", self.black + self.bold)
        format = format.replace("(reset)", self.reset)
        format = format.replace("(levelcolor)", log_color)
        format = format.replace("(green)", self.green + self.bold)
        formatter = logging.Formatter(format, "%Y-%m-%d %H:%M:%S", style="{")
        return formatter.format(record)


logger = logging.getLogger("discord_bot")
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(LoggingFormatter())
# File handler
file_handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
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
        """
        This creates custom bot variables so that we can access these variables in cogs more easily.

        For example, The logger is available using the following code:
        - self.logger # In this class
        - bot.logger # In this file
        - self.bot.logger # In cogs
        """
        self.logger = logger
        self.database = None
        self.settings = settings
        self.bot_prefix = self.settings.PREFIX
        self.invite_link = self.settings.INVITE_LINK


    async def init_db(self) -> None:
        async with aiosqlite.connect(
            f"{os.path.realpath(os.path.dirname(__file__))}/database/database.db"
        ) as db:
            with open(
                f"{os.path.realpath(os.path.dirname(__file__))}/database/schema.sql",
                encoding = "utf-8"
            ) as file:
                await db.executescript(file.read())
            await db.commit()

    async def load_cogs(self) -> None:
        """
        The code in this function is executed whenever the bot will start.
        """
        for file in os.listdir(f"{os.path.realpath(os.path.dirname(__file__))}/cogs"):
            if file.endswith(".py"):
                extension = file[:-3]
                try:
                    await self.load_extension(f"cogs.{extension}")
                    self.logger.info(f"Loaded extension '{extension}'")
                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    self.logger.error(
                        f"Failed to load extension {extension}\n{exception}"
                    )

    @tasks.loop(minutes=1.0)
    async def status_task(self) -> None:
        """
        Setup the game status task of the bot.
        """
        await self.change_presence(activity=discord.Game("keeping Ryuzen safe"))

    @status_task.before_loop
    async def before_status_task(self) -> None:
        """
        Before starting the status changing task, we make sure the bot is ready
        """
        await self.wait_until_ready()

    async def setup_hook(self) -> None:
        self.logger.info(f"Logged in as {self.user.name}")
        self.logger.info(f"discord.py API version: {discord.__version__}")
        self.logger.info(f"Python version: {platform.python_version()}")
        self.logger.info(f"Running on: {platform.system()} {platform.release()} ({os.name})")
        self.logger.info("-------------------")
        # connessione al DB
        self.database = DatabaseManager(
            connection=await aiosqlite.connect(
                f"{os.path.realpath(os.path.dirname(__file__))}/database/database.db"
            )
        )
        await self.init_db()
        await self.load_cogs()
        self.status_task.start()
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

        elif isinstance(error, commands.MissingRequiredArgument):
            embed = error_embed(
                title="W-w-wait!",
                message=str(error).capitalize() + " I need that piece to finish the spell!"
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

        else:
            await context.send(
                embed=error_embed(
                    title="Huh?",
                    message=f"Command `{context.command}`? Never heard of it! Maybe it’s hiding in a cave..."
                )
            )

if __name__ == "__main__":
    bot = DiscordBot()
    bot.run(settings.TOKEN)
