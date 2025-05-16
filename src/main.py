from config.config import settings
from src.bot import DiscordBot

if __name__ == "__main__":
    bot = DiscordBot()
    bot.run(settings.TOKEN)
