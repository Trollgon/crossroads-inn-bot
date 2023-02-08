import discord
from discord.ext import commands
from cogs.user_commands import UserCommands
from cogs.admin_commands import AdminCommands

GUILD = discord.Object(id=1071457065056354324)
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    await bot.add_cog(UserCommands(bot))
    await bot.add_cog(AdminCommands(bot))

    bot.tree.copy_global_to(guild=GUILD)
    await bot.tree.sync(guild=GUILD)
    await init_builds()


bot.run("API_KEY")