import os
import discord
from discord.ext import commands
from cogs.admin_commands import AdminCommands
from views.application_overview import ApplicationOverview
from database import init_db

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def setup_hook():
    bot.add_view(ApplicationOverview(bot))


@bot.event
async def on_ready():
    await bot.add_cog(AdminCommands(bot))
    await init_db()

bot.run(os.getenv("DISCORD_TOKEN"))