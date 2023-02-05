import discord
from discord.ext import commands
from cogs.user_commands import UserCommands
from cogs.admin_commands import AdminCommands
import asyncio
import logging

GUILD = discord.Object(id=1071457065056354324)
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    await bot.add_cog(UserCommands(bot))
    await bot.add_cog(AdminCommands(bot))

    bot.tree.copy_global_to(guild=GUILD)
    await bot.tree.sync(guild=GUILD)


bot.run("API_KEY")