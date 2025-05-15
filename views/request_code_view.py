import discord
from utils.embeds import create_embed, EMBED_COLOR_ERROR, EMBED_COLOR_INFO


class ClaimCodeButton(discord.ui.Button):
    def __init__(self, database):
        super().__init__(
            label="🎟️ Claim Code",
            style=discord.ButtonStyle.success,
            custom_id="get_code_button"  # sarà modificato dinamicamente in View
        )
        self.database = database

    async def callback(self, interaction: discord.Interaction):
        try:
            _, tournament_id = interaction.data["custom_id"].split("::")
        except Exception:
            await interaction.response.send_message(
                "❌ Unable to determine the tournament.",
                ephemeral=True
            )
            return

        server_id = interaction.guild.id
        code = await self.database.get_code(server_id, tournament_id)

        if not code:
            await interaction.response.send_message(
                embed=create_embed(
                    "❌ No Code Available",
                    f"No code set for `{tournament_id}`.",
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
                title=f"{tournament_id} – Exclusive Code",
                description="You've successfully claimed the unique code. Keep it safe and private!",
                color=EMBED_COLOR_INFO,
            )
            embed_dm.add_field(name="🔐 Code", value=f"`{code}`", inline=False)
            embed_dm.set_footer(text="Thanks for participating – Team RYUZEN")

            await interaction.user.send(embed=embed_dm)
        except discord.Forbidden:
            pass


class RequestCodeView(discord.ui.View):
    def __init__(self, database, tournament_id: str):
        super().__init__(timeout=None)
        btn = ClaimCodeButton(database)
        btn.custom_id = f"get_code_button::{tournament_id}"
        self.add_item(btn)

    @classmethod
    def create(cls, database, tournament_id: str, tournament_name: str) -> tuple[discord.Embed, "RequestCodeView"]:
        view = cls(database, tournament_id)
        embed = cls.get_announcement_embed(tournament_name)
        return embed, view

    @staticmethod
    def get_announcement_embed(tournament_name: str) -> discord.Embed:
        return (
            discord.Embed(
                title=f"{tournament_name} – Request Access Code",
                description=(
                    "Click the button below to receive **your unique access code** via DM and here.\n\n"
                    "> If DMs are disabled, you’ll still see the code here."
                ),
                color=EMBED_COLOR_INFO,
            ).set_footer(text="RYUZEN Tournament Bot")
        )
