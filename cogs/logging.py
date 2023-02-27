import datetime
import discord.ext.commands
from discord import Embed
from config import LOG_CHANNEL_ID
from gw2.models.equipment import Equipment
from gw2.models.feedback import FeedbackLevel


async def log_gear_check(bot: discord.ext.commands.Bot, interaction: discord.Interaction,
                         player_equipment: Equipment, reference_equipment: Equipment,
                         level: FeedbackLevel) -> None:
    # Log to channel
    embed = Embed(title=f"Automatic Gear Check: {level.name}",
                  description=f"**User:** {interaction.user.mention}\n"
                              f"**Build:** {reference_equipment.name}")
    embed.colour = level.colour
    embed = player_equipment.to_embed(embed)
    await log_to_channel(bot, embed)


async def log_to_channel(bot: discord.ext.commands.Bot, embed: Embed) -> None:
    embed.timestamp = datetime.datetime.now()
    await bot.get_channel(LOG_CHANNEL_ID).send(embed=embed)