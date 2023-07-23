import os
import aiohttp
import discord
from discord import Interaction, Embed
from discord.ext import commands
from sqlalchemy import select
from api import API
from database import Session
from helpers.custom_embed import CustomEmbed
from helpers.embeds import generate_error_embed
from helpers.log_checks import check_log
from helpers.logging import log_to_channel
from models.enums.log_status import LogStatus
from models.feedback import FeedbackLevel
import re
from models.log import Log
from views.log_review import LogReviewView


class SubmitLogModal(discord.ui.Modal, title="Submit log"):
    api_key: str = discord.ui.TextInput(label="API Key")
    log_url: str = discord.ui.TextInput(label="Log", min_length=40, max_length=60)

    def __init__(self, bot: commands.Bot, tier: int):
        super().__init__()
        self.bot = bot
        self.tier = tier

    async def on_submit(self, interaction: Interaction) -> None:
        self.api_key = "F1E760E8-6BFD-FA43-AFD2-C01A91FF39182A8DED37-4171-418C-A02D-CAE192B07D47"

        # Defer to prevent interaction timeout
        await interaction.response.defer(ephemeral=True, thinking=True)

        # Create embed
        embed = CustomEmbed(self.bot, title="Log Feedback", color=FeedbackLevel.ERROR.colour)

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
                        error = f"{self.log_url}\n{e}"
                else:
                    error = f"{str(self.log_url)}\n{r.status}: {r.text()}"

        if error:
            embed.add_field(name=f"{FeedbackLevel.ERROR.emoji} Error while parsing log", value=error,
                            inline=False)
            await log_to_channel(self.bot, embed)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return


        async with Session.begin() as session:
            # Check if a log for this boss was already submitted
            stmt = select(Log).where(Log.discord_user_id == interaction.user.id)\
                .where(Log.status != LogStatus.DENIED).where(Log.status != LogStatus.REVIEW_DENIED)\
                .where(Log.encounter_id == log_json["eiEncounterID"])
            if (await session.execute(stmt)).scalar():
                embed.add_field(name=f"{FeedbackLevel.ERROR.emoji} You have already submitted a log for this boss",
                                value="",
                                inline=False)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            # Check log
            fbc = check_log(log_json, await api.get_account_name())
            fbc.to_embed(embed)

            # Create log
            log = Log()
            log.discord_user_id = interaction.user.id
            log.tier = self.tier
            log.encounter_id = log_json["eiEncounterID"]
            log.fight_name = log_json["fightName"]
            log.is_cm  = log_json["isCM"]
            log.log_url = str(self.log_url)
            log.status = LogStatus.DENIED if fbc.level == FeedbackLevel.ERROR else LogStatus.WAITING_FOR_REVIEW
            session.add(log)
            await session.flush()
            await session.refresh(log)

            if log.status == LogStatus.DENIED:
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            # Create review message
            review_embed = Embed(title="Log Review",
                          description=f"{interaction.user} submitted a log to apply for tier {log.tier}.\n\n"
                                      f"[{log.fight_name}]({log.log_url})")
            fbc.to_embed(review_embed)

            # TODO: add automatic log check feedback

            message = await self.bot.get_channel(int(os.getenv("RR_CHANNEL_ID")))\
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