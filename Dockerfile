FROM python:3.12.9-slim-bookworm

WORKDIR /bot
COPY . /bot

RUN python -m pip install -r requirements.txt

# Create log file with correct permissions
RUN touch /bot/discord.log && chmod 666 /bot/discord.log

ENTRYPOINT [ "python", "bot.py" ]