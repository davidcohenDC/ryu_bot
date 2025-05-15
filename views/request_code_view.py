import discord
from utils.embeds import create_embed, EMBED_COLOR_ERROR, EMBED_COLOR_INFO

class RequestCodeView(discord.ui.View):
    def __init__(self, database, server_id: int):
        super().__init__(timeout=None)
        self.database = database
        self.server_id = server_id

    @classmethod
    def create(cls, database, server_id: int) -> tuple[discord.Embed, "RequestCodeView"]:
        """
        Factory per creare embed e view coerenti.
        """
        view = cls(database=database, server_id=server_id)
        embed = cls.get_announcement_embed()
        return embed, view

    @staticmethod
    def get_announcement_embed(
        footer_text: str = "RYUZEN Tournament Bot"
    ) -> discord.Embed:
        return (
            discord.Embed(
                title="Request Access Code",
                description=(
                    "Click the button below to receive **your unique access code** via DM and here.\n\n"
                    "> If DMs are disabled, you’ll still see the code here."
                ),
                color=EMBED_COLOR_INFO,
            )
            .set_footer(text=footer_text)
        )

    async def handle_code_claim(self, interaction: discord.Interaction):
        code = await self.database.get_code(self.server_id)

        if not code:
            await interaction.response.send_message(
                embed=create_embed(
                    "❌ No Code Available",
                    "No code has been generated yet.",
                    EMBED_COLOR_ERROR,
                ),
                ephemeral=True,
            )
            return

        # Send response
        await interaction.response.send_message(
            embed=create_embed(
                "🔐 The Code",
                f"The code is: `{code}`\n\n> A copy has also been sent to your DMs (if enabled).",
                EMBED_COLOR_INFO,
            ),
            ephemeral=True,
        )

        # Try DM
        try:
            embed_dm = discord.Embed(
                title="Exclusive Code",
                description="You've successfully claimed the unique code. Keep it safe and private!",
                color=EMBED_COLOR_INFO,
            )
            embed_dm.add_field(name="🔐 Code", value=f"`{code}`", inline=False)
            embed_dm.set_footer(text="Thanks for participating – Team RYUZEN")

            await interaction.user.send(embed=embed_dm)
        except discord.Forbidden:
            pass

    @discord.ui.button(
        label="🎟️ Claim Code", style=discord.ButtonStyle.success, custom_id="get_code_button"
    )
    async def get_code_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.handle_code_claim(interaction)
