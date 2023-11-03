import aiohttp
import discord
from discord import Interaction
from discord.ext import commands
from api import API
from database import Session
from helpers.custom_embed import CustomEmbed
from helpers.embeds import generate_error_embed, get_log_embed
from helpers.log_checks import check_log
from helpers.logging import log_to_channel
from models.config import Config
from models.enums.config_key import ConfigKey
from models.enums.log_status import LogStatus
from models.enums.role import Role
from models.feedback import FeedbackLevel
import re
from models.log import Log
from views.log_review import LogReviewView


class SubmitLogModal(discord.ui.Modal, title="Submit log"):
    api_key: str = discord.ui.TextInput(label="API Key")
    log_url: str = discord.ui.TextInput(label="Log", min_length=40, max_length=60)

    def __init__(self, bot: commands.Bot, tier: int, role: Role):
        super().__init__()
        self.bot = bot
        self.tier = tier
        self.role = role

    async def on_submit(self, interaction: Interaction) -> None:
        # Defer to prevent interaction timeout
        await interaction.response.defer(ephemeral=True, thinking=True)

        # Create embed
        embed = CustomEmbed(self.bot, title="Log Feedback", color=FeedbackLevel.ERROR.colour)
        embed.description = f"**User:** {interaction.user}\n**Log:** {self.log_url}\n**Tier:** {self.tier}\n**Role:** {self.role.value}"

        # Check if log url is valid
        pattern = re.compile("https:\/\/dps\.report\/[a-zA-Z\-0-9\_]+")
        if not pattern.match(str(self.log_url)):
            embed.add_field(name=f"{FeedbackLevel.ERROR.emoji} Invalid log url", value="",
                            inline=False)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # Check API Key
        api = API(str(self.api_key))
        key_feedback = await api.check_key()
        embed = key_feedback.to_embed(embed)
        if key_feedback.level == FeedbackLevel.ERROR:
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # Check KP
        kp_feedback = await api.check_kp(self.tier)
        embed = kp_feedback.to_embed(embed)
        if kp_feedback.level == FeedbackLevel.ERROR:
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # Get json data from dps.report
        error = ""
        async with aiohttp.ClientSession() as session:
            async with session.get("https://dps.report/getJson?permalink=" + str(self.log_url)) as r:
                if r.status == 200:
                    try:
                        log_json = await r.json()
                    except Exception as e:
                        error = f"{str(self.log_url)}\n{e}"
                else:
                    error = f"{str(self.log_url)}\n{r.status}: {await r.text()}"

        if error:
            embed.add_field(name=f"{FeedbackLevel.ERROR.emoji} Error while parsing log", value=error,
                            inline=False)
            await log_to_channel(self.bot, embed)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # Create log
        log = Log()
        log.discord_user_id = interaction.user.id
        log.tier = self.tier
        log.role = self.role
        log.encounter_id = log_json["eiEncounterID"]
        log.fight_name = log_json["fightName"]
        log.is_cm = log_json["isCM"]
        log.log_url = str(self.log_url)

        # Check log
        fbc = await check_log(log_json, await api.get_account_name(), self.tier, interaction.user.id, str(self.log_url), log)
        fbc.to_embed(embed)
        if fbc.level == FeedbackLevel.SUCCESS:
            embed.add_field(name="Log successfully submitted for manual review", value="", inline=False)

        log.status = LogStatus.DENIED if fbc.level == FeedbackLevel.ERROR else LogStatus.WAITING_FOR_REVIEW

        async with Session.begin() as session:
            session.add(log)
            await session.flush()
            await session.refresh(log)

            if log.status == LogStatus.DENIED:
                await interaction.followup.send(embed=embed, ephemeral=True)
                await log_to_channel(self.bot, embed)
                return

            # Create review message
            review_embed = get_log_embed(str(self.log_url), log_json, interaction.user, await api.get_account_name(), self.role, self.tier)
            fbc.to_embed(review_embed)

            message = await self.bot.get_channel(int(await Config.get_value(session, ConfigKey.LOG_REVIEW_CHANNEL_ID)))\
                .send(embed=review_embed, view=LogReviewView(self.bot, log.id))
            log.review_message_id = message.id
            session.add(log)
        await interaction.followup.send(embed=embed, ephemeral=True)



    async def on_error(self, interaction: Interaction, error: Exception) -> None:
        await interaction.followup.send(embed=generate_error_embed(error), ephemeral=True)
        # Log error
        await super().on_error(interaction, error)


class LogFeedbackView(discord.ui.View):
    def __init__(self, bot: commands.Bot, api: API):
        super().__init__()
        self.bot = bot
        self.api = api
        self.original_message = None

    async def init(self):
        pass

    async def on_error(self, interaction: Interaction, error: Exception, item: discord.ui.Item) -> None:
        await self.original_message.edit(content=None, view=None, embed=generate_error_embed(error))
        # Log error
        await super().on_error(interaction, error, item)
