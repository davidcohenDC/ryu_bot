import discord
from discord import Interaction
from discord.ui import Button, View

from utils.embeds import create_embed, EMBED_COLOR_ERROR, EMBED_COLOR_INFO
from services.tournament_service import TournamentService  # Usa il service anziché accedere direttamente al database


class ClaimCodeButton(Button):
    def __init__(self, service: TournamentService, tournament_id: int):
        super().__init__(
            label="🎟️ Claim Code",
            style=discord.ButtonStyle.success,
            custom_id=f"get_code_button::{tournament_id}"
        )
        self.service = service
        self.tournament_id = tournament_id

    async def callback(self, interaction: Interaction):
        server_id = interaction.guild.id

        try:
            code = await self.service.get_code(server_id, self.tournament_id)
        except Exception:
            await interaction.response.send_message(
                embed=create_embed(
                    "❌ Error",
                    "An unexpected error occurred while retrieving the code.",
                    EMBED_COLOR_ERROR
                ),
                ephemeral=True
            )
            return

        if not code:
            await interaction.response.send_message(
                embed=create_embed(
                    "❌ No Code Available",
                    f"No code set for tournament `{self.tournament_id}`.",
                    EMBED_COLOR_ERROR
                ),
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            embed=create_embed(
                "🔐 Your Code",
                f"The code is: `{code}`\n\n> A copy has also been sent to your DMs (if enabled).",
                EMBED_COLOR_INFO
            ),
            ephemeral=True
        )

        try:
            embed_dm = discord.Embed(
                title="🎟️ Exclusive Tournament Code",
                description="You've successfully claimed the code. Keep it safe!",
                color=EMBED_COLOR_INFO,
            )
            embed_dm.add_field(name="🔐 Code", value=f"`{code}`", inline=False)
            embed_dm.set_footer(text="Thanks for participating – Team RYUZEN")

            await interaction.user.send(embed=embed_dm)
        except discord.Forbidden:
            # User has DMs off — silently fail
            pass


class RequestCodeView(View):
    def __init__(self, service: TournamentService, tournament_id: int, timeout: float | None = None):
        super().__init__(timeout=timeout)
        self.add_item(ClaimCodeButton(service, tournament_id))

    @classmethod
    def create(cls, service: TournamentService, tournament_id: int, tournament_name: str) -> tuple[discord.Embed, View]:
        view = cls(service, tournament_id)
        embed = cls.get_announcement_embed(tournament_name)
        return embed, view

    @staticmethod
    def get_announcement_embed(tournament_name: str) -> discord.Embed:
        return (
            discord.Embed(
                title=f"{tournament_name} – Request Access Code",
                description=(
                    "Click the button below to receive your unique code via DM and here.\n"
                    "> If DMs are disabled, you’ll still see the code here."
                ),
                color=EMBED_COLOR_INFO,
            ).set_footer(text="RYUZEN Tournament Bot")
        )
