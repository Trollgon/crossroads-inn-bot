import os
import discord
from discord.ext import commands
from sqlalchemy import select
from cogs.admin_commands import AdminCommands
from models.application import Application
from models.enums.application_status import ApplicationStatus
from views.application_overview import ApplicationOverview
from database import init_db, Session
from views.review import ReviewView

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
    async with Session.begin() as session:
        stmt = select(Application).where(Application.status == ApplicationStatus.WAITING_FOR_REVIEW)
        applications = (await session.execute(stmt)).scalars()
        for application in applications:
            bot.add_view(ReviewView(bot, application.id))

bot.run(os.getenv("DISCORD_TOKEN"))