import os
import re
from typing import Union

import discord
from discord.ext import commands
from discord.ext.commands import Context
import random

# === CONFIGURATION ===
ANNOUNCE_CHANNEL_NAME = "log"
ALLOWED_ROLES = ["Owner", "RyuZen Team"]
ALLOWED_COMMAND_CHANNEL_NAME = "bot-control"
TRAINERS_ROLE_NAME = "Trainer"
WINNER_ROLE_NAME = "Tournament Winner"
WINNERS_CHANNEL_ID = 1371887546014892123
RYU_EMOJI = "<:ryu:1371834896250830928>"

EMBED_COLOR_SUCCESS = 0x57F287
EMBED_COLOR_ERROR = 0xE02B2B
EMBED_COLOR_INFO = 0x5865F2

# === MOTIVATIONAL FACTS (Swiss only) ===
FACTS = [
    "🔥 *'Every duel is a step toward glory!'*",
    "🌟 *'Only one can be the very best, like no one ever was.'*",
    "⚡ *'Your next top cut might start now… prepare yourself!'*",
    "🧠 *'Mind games win matches. Stay sharp, Trainers.'*",
    "💥 *'One turn can change everything. Don't blink.'*",
    "🎯 *'Precision. Focus. Victory. One turn at a time.'*",
    "🃏 *'Trust your deck. Trust your instincts.'*",
    "🔥 *'Legends are born in rounds like this.'*",
    "🏆 *'You didn’t come this far to only come this far.'*",
    "⏳ *'Tick tock. Every second counts.'*"
    "🎮 *'Every round is a badge—collect them with honor!'*",
    "🧬 *'Synergy wins games. Respect your combos.'*",
    "🛡 *'Defense isn’t passive. It's just planning ahead.'*",
    "🧠 *'Reading your opponent is as important as reading your cards.'*",
    "🎲 *'Topdeck luck? Maybe. Preparation? Definitely.'*",
    "🌪 *'The board can change in one turn. Never let your guard down.'*",
    "🔥 *'Your starter Pokémon isn’t your fate—it’s your first step.'*",
    "🌀 *'Prize cards are temporary. Strategy is permanent.'*",
    "🎯 *'Control the tempo, control the game.'*",
    "🥇 *'Victory doesn’t depend on the cards—but how you play them.'*",
    "🍵 *'Take a sip, shuffle tight, and breathe. Round’s about to start.'*",
    "🧃 *'Drink water, not salt. Round 2 is just the beginning.'*",
    "🧦 *'Lucky socks won't help… but wear them anyway.'*",
    "🧹 *'Did you topdeck? Or just clean play? Let them wonder.'*",
    "🥶 *'Keep your cool. Your deck already knows what to do.'*",
    "📖 *'A true Trainer adapts—not only their deck, but their mindset.'*",
    "🔍 *'Observe. Predict. Play. The three rules of a master.'*",
    "🧭 *'No path to victory is straight. Be ready to pivot.'*",
    "🐾 *'Even a Caterpie can flip the script. Believe in every card.'*",
    "⚖️ *'Play fair. Play smart. Play like a Champion.'*"
    "🪙 *'Flipping a coin is luck. Playing around it is skill.'*",
    "🌈 *'Versatility wins more than brute force—tech your choices wisely.'*",
    "📦 *'Every card in your deck has a reason. Let it shine when it matters.'*",
    "🧭 *'A clear win condition is your compass. Don’t lose it in the fog of battle.'*",
    "🔄 *'Game state changes. Champions adapt. Every turn is a chance to rewrite the match.'*"
]

def get_random_fact():
    return random.choice(FACTS)

def extract_clean_title(title: str) -> str:
    # Cerca parole come "ROUND 1", "FINAL SWISS ROUND", ecc.
    match = re.search(r"(ROUND \d+|FINAL SWISS ROUND|QUARTER FINALS|SEMI FINALS|FINALS|TOP \d+)", title.upper())
    return match.group(0).title() if match else title

def format_announcement(title: str, mention: str, fun_fact: bool = False, note: str = "") -> str:
    clean = extract_clean_title(title)
    msg = f"{title}\n\n Hey {mention}! **{clean} is now LIVE!** Prepare to check-in!"
    if note:
        msg += f"\n\n {note}"
    if fun_fact:
        msg += f"\n\n> {get_random_fact()}"
    return msg

# === UTILS ===
def create_embed(title: str, description: str, color: int) -> discord.Embed:
    return discord.Embed(title=title, description=description, color=color)

def has_permission(ctx: Context) -> bool:
    if ctx.author.id == ctx.bot.owner_id:
        return True
    user_roles = [role.name for role in ctx.author.roles]
    return any(role in ALLOWED_ROLES for role in user_roles)

def is_correct_channel(ctx: Context) -> bool:
    return ctx.channel.name == ALLOWED_COMMAND_CHANNEL_NAME


def resolve_member_mention(guild: discord.Guild, user_input: str, *, return_input_if_not_found: bool = False) -> Union[
    str, discord.Member]:
    """Restituisce un membro se trovato, altrimenti una stringa o None in base alla flag."""
    cleaned_input = user_input.strip("<@!>")

    member = None
    if cleaned_input.isdigit():
        member = guild.get_member(int(cleaned_input))
    else:
        member = discord.utils.find(
            lambda m: cleaned_input.lower() in [m.name.lower(), m.display_name.lower()],
            guild.members
        )

    if member:
        return member
    return user_input if return_input_if_not_found else None

# === TOURNAMENT SCHEDULER ===
class TournamentManager:
    def __init__(self):
        self.total_swiss = 0
        self.top_cut = 0
        self.current_round = 0
        self.announcements = []
        self.trainers_role_id = None
        self.tournament_name = None


    def set_tournament_name(self, name: str):
        self.tournament_name = name.strip()

    def is_initialized(self) -> bool:
        return self.tournament_name is not None

    def set_trainers_role(self, guild: discord.Guild, role_name: str = TRAINERS_ROLE_NAME):
        role = discord.utils.get(guild.roles, name=role_name)
        if role:
            self.trainers_role_id = role.id

    def build_schedule(self, total_swiss: int, top_cut: int):
        self.total_swiss = total_swiss
        self.top_cut = top_cut
        self.current_round = 0
        self.announcements = []

        if total_swiss <= 0:
            raise ValueError("Swiss rounds must be at least 1")

        mention = f"<@&{self.trainers_role_id}>" if self.trainers_role_id else "@Trainers"
        mid_swiss = total_swiss // 2

        # Swiss rounds
        for i in range(1, total_swiss + 1):
            round_title = f"# ⟪ ROUND {i} ⟫"
            note = ""
            if i == mid_swiss:
                note = "We're halfway through the Swiss rounds!"
            elif i == total_swiss:
                round_title = "# FINAL SWISS ROUND"
                note = "This is the final Swiss round – make it count!"

            message = format_announcement(round_title, mention, fun_fact=True, note=note)
            self.announcements.append(message)

        # Top Cut
        if top_cut > 0:
            rounds = top_cut.bit_length() - 1
            sizes = [f"Top {2 ** (rounds - i)}" for i in range(rounds)]

            label_map = {
                4: "Finals",
                8: "Semi Finals",
                16: "Quarter Finals",
                32: "Top 16",
                64: "Top 32",
            }

            for size in sizes:
                label = label_map.get(int(size.split()[1]), size)
                round_title = f"# {label.upper()}"
                message = format_announcement(round_title, mention, fun_fact=False)
                self.announcements.append(message)

    def get_next_announcement(self):
        if self.current_round >= len(self.announcements):
            return None

        # Controlla se il round corrente è "Finals"
        next_announcement = self.announcements[self.current_round]
        if "FINALS" in next_announcement.upper():
            self.current_round += 1  # annuncia le Finals una sola volta
            return next_announcement

        # Se abbiamo già annunciato le Finals, non si va oltre
        if self.current_round > 0 and "FINALS" in self.announcements[self.current_round - 1].upper():
            return None

        announcement = self.announcements[self.current_round]
        self.current_round += 1
        return announcement

    def jump_to(self, index: int) -> str:
        if 0 <= index < len(self.announcements):
            self.current_round = index
            return self.announcements[self.current_round]
        raise IndexError("Index out of range of scheduled rounds.")


# === INTERACTIVE VIEW WITH BUTTON ===
class RoundControlView(discord.ui.View):
    def __init__(self, bot, manager: TournamentManager):
        super().__init__(timeout=None)
        self.bot = bot
        self.manager = manager

    @discord.ui.button(label="➡️ Avanza Round", style=discord.ButtonStyle.primary)
    async def advance_round(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.bot.owner_id and not any(role.name in ALLOWED_ROLES for role in interaction.user.roles):
            await interaction.response.send_message("🚫 Non hai i permessi per usare questo pulsante.", ephemeral=True)
            return

        message = self.manager.get_next_announcement()
        if not message:
            await interaction.response.send_message("❌ Tutti i round sono già stati annunciati.", ephemeral=True)
            return

        announce_channel = discord.utils.get(interaction.guild.text_channels, name=ANNOUNCE_CHANNEL_NAME)
        if not announce_channel:
            await interaction.response.send_message(f"❌ Canale `#{ANNOUNCE_CHANNEL_NAME}` non trovato.", ephemeral=True)
            return

        await announce_channel.send(message, allowed_mentions=discord.AllowedMentions(roles=True))
        await interaction.response.send_message("✅ Round annunciato!", ephemeral=True)


# === COG ===
class RoundAnnouncer(commands.Cog, name="Round Announcer"):
    def __init__(self, bot):
        self.bot = bot
        self.manager = TournamentManager()



    @commands.hybrid_command(name="start_tournament",
                             description="Initialize tournament structure with Swiss and Top Cut rounds.")
    async def start_tournament(self, ctx: Context, tournament_name: str = None, swiss: int = None, top_cut: int = 0):
        if not has_permission(ctx):
            await ctx.send(
                embed=create_embed("🚫 Permission Denied", f"You must be the bot owner or have one of the following roles: {', '.join(ALLOWED_ROLES)}.", EMBED_COLOR_ERROR),
                ephemeral=True
            )
            return

        if tournament_name is None or len(tournament_name) < 3:
            await ctx.send(
                embed=create_embed("⚠️ Missing Argument", "You must specify a valid tournament name (at least 3 characters).", EMBED_COLOR_ERROR),
                ephemeral=True
            )
            return

        if not is_correct_channel(ctx):
            await ctx.send(
                embed=create_embed("📛 Wrong Channel", f"This command can only be used in `#{ALLOWED_COMMAND_CHANNEL_NAME}`.", EMBED_COLOR_ERROR),
                ephemeral=True
            )
            return

        if swiss is None or swiss <= 0:
            await ctx.send(embed=create_embed("⚠️ Missing Argument", "You must specify a valid number of Swiss rounds (1 or more).", EMBED_COLOR_ERROR), ephemeral=True)
            return

        self.manager.set_trainers_role(ctx.guild)
        self.manager.set_tournament_name(tournament_name)

        if not self.manager.trainers_role_id:
            await ctx.send(embed=create_embed("⚠️ Role Not Found", f"Could not find a role named `{TRAINERS_ROLE_NAME}`.", EMBED_COLOR_ERROR), ephemeral=True)
            return

        try:
            self.manager.build_schedule(swiss, top_cut)
        except Exception as e:
            await ctx.send(embed=create_embed("❌ Error", str(e), EMBED_COLOR_ERROR), ephemeral=True)
            return

        await ctx.send(
            embed=create_embed("✅ Tournament Initialized",
                               f"**{tournament_name}** started!\nStructure: {swiss} Swiss round(s) + Top Cut {top_cut if top_cut else 'disabled'}.",
                               EMBED_COLOR_SUCCESS),
            view=RoundControlView(self.bot, self.manager),
            ephemeral=False
        )

    @commands.hybrid_command(name="post_winner_deck",
                             description="Invia l'immagine del mazzo vincente in #deck-winners.")
    async def post_winner_deck(self, ctx: Context, player: str, no_check: bool = False):
        if not has_permission(ctx):
            await ctx.send(embed=create_embed("🚫 Permission Denied",
                                              "Solo gli admin possono usare questo comando.",
                                              EMBED_COLOR_ERROR), ephemeral=True)
            return

        if not self.manager.is_initialized():
            await ctx.send(embed=create_embed("⚠️ Tournament Not Set",
                                              "Devi prima avviare un torneo con `/start_tournament`.",
                                              EMBED_COLOR_ERROR), ephemeral=True)
            return

        if not ctx.message.attachments:
            await ctx.send(embed=create_embed("⚠️ Nessuna immagine",
                                              "Devi allegare un'immagine del mazzo.",
                                              EMBED_COLOR_ERROR), ephemeral=True)
            return

        if no_check:
            mention = player
        else:
            result = resolve_member_mention(ctx.guild, player, return_input_if_not_found=False)
            if not isinstance(result, discord.Member):
                await ctx.send(embed=create_embed("❌ Membro non trovato",
                                                  f"Non riesco a trovare il giocatore `{player}` nel server.",
                                                  EMBED_COLOR_ERROR), ephemeral=True)
                return
            member = result
            mention = member.mention

        # 📥 Recupero allegato
        file = ctx.message.attachments[0]
        if not file.filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            await ctx.send(embed=create_embed("⚠️ File non valido",
                                              "Devi allegare un file immagine (.png, .jpg, .jpeg, .webp).",
                                              EMBED_COLOR_ERROR), ephemeral=True)
            return

        image_file = await file.to_file()
        deck_channel = ctx.guild.get_channel(WINNERS_CHANNEL_ID)
        if not deck_channel:
            await ctx.send(embed=create_embed("❌ Channel Not Found",
                                              f"Canale con ID `{WINNERS_CHANNEL_ID}` non trovato.",
                                              EMBED_COLOR_ERROR), ephemeral=True)
            return

        # 🏆 Composizione messaggio
        tournament_name = self.manager.tournament_name
        message_content = (
            f"# 🏆 Winner of **{tournament_name}**\n"
            f"> **Player:** {mention}"
        )

        await deck_channel.send(content=message_content, file=image_file)
        await ctx.send(embed=create_embed("✅ Deck pubblicato",
                                          f"Deck di {mention} caricato in <#{WINNERS_CHANNEL_ID}>.",
                                          EMBED_COLOR_SUCCESS), ephemeral=True)

    @commands.hybrid_command(name="clear_tournament", description="Termina e resetta il torneo attivo.")
    async def clear_tournament(self, ctx: Context):
        if not has_permission(ctx):
            await ctx.send(
                embed=create_embed("🚫 Permission Denied",
                                   "Solo gli admin possono terminare il torneo.",
                                   EMBED_COLOR_ERROR),
                ephemeral=True
            )
            return

        if not self.manager.is_initialized():
            await ctx.send(
                embed=create_embed("⚠️ Nessun Torneo Attivo",
                                   "Non c'è alcun torneo attivo al momento.",
                                   EMBED_COLOR_INFO),
                ephemeral=True
            )
            return

        # Reset dei dati del torneo
        self.manager = TournamentManager()

        await ctx.send(
            embed=create_embed("🛑 Torneo Eliminato",
                               "Il torneo è stato eliminato con successo. Tutti i dati sono stati resettati.",
                               EMBED_COLOR_SUCCESS),
            ephemeral=False
        )

    @commands.hybrid_command(name="declare_winner", description="Dichiara il vincitore del torneo.")
    async def declare_winner(self, ctx: Context, winner: str, no_check: bool = False):
        if not has_permission(ctx):
            await ctx.send(
                embed=create_embed("🚫 Permission Denied", "Solo gli admin possono dichiarare il vincitore.",
                                   EMBED_COLOR_ERROR),
                ephemeral=True
            )
            return
        if not self.manager.is_initialized():
            await ctx.send(embed=create_embed("⚠️ Tournament Not Set",
                                              f"Devi prima avviare un torneo con `{os.getenv('PREFIX')}start_tournament` per dichiarare il vincitore.",
                                              EMBED_COLOR_ERROR), ephemeral=True)
            return
        if not is_correct_channel(ctx):
            await ctx.send(
                embed=create_embed("📛 Wrong Channel",
                                   f"Questo comando può essere usato solo in `#{ALLOWED_COMMAND_CHANNEL_NAME}`.",
                                   EMBED_COLOR_ERROR),
                ephemeral=True
            )
            return

        if no_check:
            mention = winner
        else:
            result = resolve_member_mention(ctx.guild, winner, return_input_if_not_found=False)
            if not isinstance(result, discord.Member):
                await ctx.send(embed=create_embed("❌ Membro non trovato",
                                                  f"Non riesco a trovare il giocatore `{winner}` nel server.",
                                                  EMBED_COLOR_ERROR), ephemeral=True)
                return
            member = result
            mention = member.mention

        # 📢 Canale di annuncio
        announce_channel = discord.utils.get(ctx.guild.text_channels, name=ANNOUNCE_CHANNEL_NAME)
        if not announce_channel:
            await ctx.send(embed=create_embed("❌ Channel Not Found", f"Canale `#{ANNOUNCE_CHANNEL_NAME}` non trovato.",
                                              EMBED_COLOR_ERROR), ephemeral=True)
            return

        # 🏷️ Ruolo vincitore
        winner_role = discord.utils.get(ctx.guild.roles, name=WINNER_ROLE_NAME)
        if not winner_role:
            await ctx.send(embed=create_embed("❌ Role Not Found", f"Ruolo `{WINNER_ROLE_NAME}` non trovato.",
                                              EMBED_COLOR_ERROR), ephemeral=True)
            return

        # 🎖 Assegna ruolo
        try:
            await member.add_roles(winner_role, reason="Ha vinto il torneo.")
        except discord.Forbidden:
            await ctx.send(embed=create_embed("❌ Permesso Negato", "Non posso assegnare il ruolo al vincitore.",
                                              EMBED_COLOR_ERROR), ephemeral=True)
            return

        # 🥳 Messaggio finale
        congratulations = (
            f"# {RYU_EMOJI} Congratulations {mention}! {RYU_EMOJI}\n"
            f"**You are the CHAMPION of `{self.manager.tournament_name}`!!** 🏅\n\n"
            f"**What you earn:**\n"
            f"1. Limitless official 1st position *(check it in your History on Limitless)*\n"
            f"2. **Enjoy your new role on Ryuzen: {winner_role.mention} !!!**\n"
            f"3. Your deck will also be added to <#{WINNERS_CHANNEL_ID}>"
        )

        message = await announce_channel.send(congratulations)

        try:
            await message.add_reaction(f"{RYU_EMOJI}")
        except discord.HTTPException:
            pass

        await ctx.send(embed=create_embed("✅ Vincitore Annunciato",
                                          f"{member.mention} è stato celebrato e ha ricevuto il ruolo `{WINNER_ROLE_NAME}`.",
                                          EMBED_COLOR_SUCCESS), ephemeral=True)



    @commands.hybrid_command(name="next_round", description="Announce the next round in the tournament.")
    async def next_round(self, ctx: Context):
        if not has_permission(ctx):
            await ctx.send(
                embed=create_embed("🚫 Permission Denied", f"You must be the bot owner or have one of the following roles: {', '.join(ALLOWED_ROLES)}.", EMBED_COLOR_ERROR),
                ephemeral=True
            )
            return

        if not is_correct_channel(ctx):
            await ctx.send(
                embed=create_embed("📛 Wrong Channel", f"This command can only be used in `#{ALLOWED_COMMAND_CHANNEL_NAME}`.", EMBED_COLOR_ERROR),
                ephemeral=True
            )
            return

        message = self.manager.get_next_announcement()

        if not message:
            await ctx.send(
                embed=create_embed("❌ No More Rounds", "All rounds have already been announced.", EMBED_COLOR_ERROR),
                ephemeral=True
            )
            return

        announce_channel = discord.utils.get(ctx.guild.text_channels, name=ANNOUNCE_CHANNEL_NAME)
        if not announce_channel:
            await ctx.send(
                embed=create_embed("❌ Channel Not Found", f"Please create a channel named `#{ANNOUNCE_CHANNEL_NAME}`.", EMBED_COLOR_ERROR),
                ephemeral=True
            )
            return

        await announce_channel.send(message, allowed_mentions=discord.AllowedMentions(roles=True))
        await ctx.send(embed=create_embed("✅ Round Announced", f"Message sent to `#{ANNOUNCE_CHANNEL_NAME}`.", EMBED_COLOR_SUCCESS), ephemeral=True)

    @commands.hybrid_command(name="set_round", description="Manually set the current round index.")
    async def set_round(self, ctx: Context, index: int = None):
        if not has_permission(ctx):
            await ctx.send(
                embed=create_embed("🚫 Permission Denied", f"You must be the bot owner or have one of the following roles: {', '.join(ALLOWED_ROLES)}.", EMBED_COLOR_ERROR),
                ephemeral=True
            )
            return

        if not is_correct_channel(ctx):
            await ctx.send(
                embed=create_embed("📛 Wrong Channel", f"This command can only be used in `#{ALLOWED_COMMAND_CHANNEL_NAME}`.", EMBED_COLOR_ERROR),
                ephemeral=True
            )
            return

        if index is None:
            await ctx.send(embed=create_embed("⚠️ Missing Argument", "You must specify the round index to jump to.", EMBED_COLOR_ERROR), ephemeral=True)
            return

        try:
            message = self.manager.jump_to(index)
            await ctx.send(embed=create_embed("✅ Round Set", f"Next round announcement set to index `{index}`:\n\n{message}", EMBED_COLOR_SUCCESS), ephemeral=True)
        except IndexError:
            await ctx.send(embed=create_embed("❌ Invalid Index", "Index is out of range.", EMBED_COLOR_ERROR), ephemeral=True)

    @start_tournament.error
    @next_round.error
    @set_round.error
    async def command_error_handler(self, ctx: Context, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(embed=create_embed("❌ Internal Error", str(error), EMBED_COLOR_ERROR), ephemeral=True)
        else:
            raise error

async def setup(bot):
    await bot.add_cog(RoundAnnouncer(bot))
