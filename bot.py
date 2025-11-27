import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
import asyncio

TOKEN = "MTQ0MzQ1Nzk2Njg0OTM5NjkzNw.GtePpE.eJL2IlNZUhK5HEnMvmp5vd9amLAey5Fqz67MhU"  # GANTI INI

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

ticket_count = 0
BAD_WORDS = ["fuck","shit","bitch","asshole","dick","wtf","kys",
             "nigger","fucker","bs","bullshit","pussy","motherfucker"]

# ===================================================
# ANTI TOXIC
# ===================================================
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.lower()
    if any(word in content for word in BAD_WORDS):
        try:
            await message.author.timeout(discord.utils.utcnow() + discord.timedelta(minutes=5),
                                        reason="Toxic words")
            await message.channel.send(f"{message.author.mention} muted **5 minutes** (toxic).")
        except:
            pass

    await bot.process_commands(message)

# ===================================================
# AUTO FIND OR CREATE CATEGORY
# ===================================================
async def get_ticket_category(guild: discord.Guild):
    category = discord.utils.get(guild.categories, name="🎟️ Tickets")
    if category is None:
        category = await guild.create_category("🎟️ Tickets")
    return category

# ===================================================
# CREATE TICKET BUTTON
# ===================================================
class CreateTicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Create Ticket 🎟️", style=discord.ButtonStyle.green)
    async def create_ticket(self, interaction: discord.Interaction, button: Button):
        global ticket_count
        ticket_count += 1

        category = await get_ticket_category(interaction.guild)

        ticket_channel = await category.create_text_channel(f"ticket-{ticket_count}")
        await ticket_channel.set_permissions(interaction.user, view_channel=True, send_messages=True)

        await interaction.response.send_message(
            f"Your ticket has been created: **#{ticket_count}**",
            ephemeral=True
        )

        view = CloseTicketView()
        await ticket_channel.send(
            f"**Welcome To Tickets, Let's chat!**\n{interaction.user.mention}",
            view=view
        )

# ===================================================
# CLOSE TICKET
# ===================================================
class CloseTicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket ✅", style=discord.ButtonStyle.red)
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Closing ticket in 3...", ephemeral=True)
        await asyncio.sleep(1)
        await interaction.edit_original_response(content="Closing ticket in 2...")
        await asyncio.sleep(1)
        await interaction.edit_original_response(content="Closing ticket in 1...")
        await asyncio.sleep(1)

        await interaction.channel.delete(reason="Ticket closed")

# ===================================================
# SEND PANEL
# ===================================================
@bot.tree.command(name="ticketpanel", description="Send ticket panel")
async def ticketpanel(interaction: discord.Interaction):
    view = CreateTicketView()
    await interaction.response.send_message(
        "**Sheriff Tickets Helps You Contact Staff Without DMs. Safer to Use @SheriffTickets**",
        view=view
    )

# ===================================================
# /unmute COMMAND
# ===================================================
@bot.tree.command(name="unmute", description="Unmute a user")
async def unmute(interaction: discord.Interaction, member: discord.Member):
    if not interaction.user.guild_permissions.kick_members:
        return await interaction.response.send_message("No permission.", ephemeral=True)

    await member.timeout(None)
    await interaction.response.send_message(f"{member.mention} is now unmuted.")

# ===================================================
# READY
# ===================================================
@bot.event
async def on_ready():
    print(f"Bot Online as {bot.user}")
    try:
        await bot.tree.sync()
        print("Slash commands synced.")
    except Exception as e:
        print(e)

bot.run(TOKEN)
