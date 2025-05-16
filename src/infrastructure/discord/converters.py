from discord.ext import commands
from src.domains.tournament.models import Tournament


class TournamentConverter(commands.Converter):
    async def convert(self, ctx: commands.Context, argument: str) -> Tournament:
        try:
            tournament_id = int(argument)
        except ValueError:
            raise commands.BadArgument("Tournament ID must be a number.")

        service = ctx.cog.service
        tournaments = await service.get_by_id(ctx.guild.id,tournament_id)
        return tournaments