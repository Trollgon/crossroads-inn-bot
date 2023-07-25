import datetime
import discord.ext.commands
from discord import Embed

from database import Session
from models.build import Build
from models.config import Config
from models.enums.config_key import ConfigKey
from models.equipment import Equipment
from models.feedback import FeedbackCollection


async def log_gear_check(bot: discord.ext.commands.Bot, interaction: discord.Interaction,
                         equipment: Equipment, build: Build,
                         feedback: FeedbackCollection) -> None:
    # Log to channel
    embed = Embed(title=f"Automatic Gear Check: {feedback.level.name}",
                  description=f"**User:** {interaction.user}\n"
                              f"**Build:** {build.to_link()}")
    embed.colour = feedback.level.colour
    embed = equipment.to_embed(embed)
    embed = feedback.to_embed(embed)
    await log_to_channel(bot, embed)


async def log_to_channel(bot: discord.ext.commands.Bot, embed: Embed) -> None:
    embed.timestamp = datetime.datetime.now()
    async with Session.begin() as session:
        log_channel_id = int((await Config.get_value(session, ConfigKey.LOG_CHANNEL_ID)))
        await bot.get_channel(log_channel_id).send(embed=embed)