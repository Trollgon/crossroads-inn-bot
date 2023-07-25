import discord
from discord import Interaction, ButtonStyle, Embed
from discord.ext import commands
from discord.ui import View, Modal
from sqlalchemy import select, func

from database import Session
from helpers.emotes import get_random_success_emote
from models.config import Config
from models.enums.config_key import ConfigKey
from models.enums.log_status import LogStatus
from models.log import Log
from views.callback_button import CallbackButton
from helpers.logging import log_to_channel


class LogReviewView(View):
    def __init__(self, bot: commands.Bot, log_id: int):
        super().__init__(timeout=None)
        self.bot = bot
        self.log_id = log_id
        self.add_item(CallbackButton(self.accept, label="Accept", style=ButtonStyle.green,
                                     custom_id=f"{self.bot.user.id}-application-{log_id}:accept"))
        self.add_item(CallbackButton(self.deny, label="Deny", style=ButtonStyle.red,
                                     custom_id=f"{self.bot.user.id}-application-{log_id}:deny"))
    async def accept(self, interaction: Interaction):
        await interaction.response.send_modal(LogReviewModal(self.bot, LogStatus.REVIEW_ACCEPTED, self.log_id, self))

    async def deny(self, interaction: Interaction):
        await interaction.response.send_modal(LogReviewModal(self.bot, LogStatus.REVIEW_DENIED, self.log_id, self))
    async def on_error(self, interaction: Interaction, error: Exception, item: discord.ui.Item) -> None:
        # Send message to user and log error
        await interaction.response.send_message(ephemeral=True, content="An unknown error occured. Please try again later.")
        await super().on_error(interaction, error, item)


class LogReviewModal(Modal, title="Log review"):
    feedback = discord.ui.TextInput(label="Feedback", style=discord.TextStyle.paragraph)

    def __init__(self, bot: commands.Bot, status: LogStatus, log_id: int, parent_view: View):
        self.bot = bot
        self.log_id = log_id
        self.parent_view = parent_view
        self.status = status

        match status:
            case LogStatus.REVIEW_ACCEPTED:
                self.feedback.default = "Your log has been accepted"
            case LogStatus.REVIEW_DENIED:
                self.feedback.default = "Your log has been denied"

        super().__init__()

    async def on_submit(self, interaction: Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        async with Session.begin() as session:
            log: Log = await session.get(Log, self.log_id)
            # Make sure application has not been handled already
            if log.status != LogStatus.WAITING_FOR_REVIEW:
                reviewer = self.bot.get_user(log.reviewer)
                await interaction.followup.send(content=f"This log has already been {log.status} by {reviewer.mention}", ephemeral=True)
                return

            # Send feedback message
            emote = ""
            role_assignment_text = ""
            ta_channel = interaction.guild.get_channel(int(await Config.get_value(session, ConfigKey.TIER_ASSIGNMENT_CHANNEL_ID)))
            rr_channel = interaction.guild.get_channel(int(await Config.get_value(session, ConfigKey.RR_CHANNEL_ID)))
            member = interaction.guild.get_member(log.discord_user_id)
            if self.status == LogStatus.REVIEW_ACCEPTED:
                roles = []
                stmt = select(func.count(Log.id)).where(Log.discord_user_id == log.discord_user_id)\
                    .where(Log.status == LogStatus.REVIEW_ACCEPTED).where(Log.tier == log.tier)\
                    .where(Log.role == log.role)
                if log.tier == 2 and (await session.execute(stmt)).scalar() + 1 >= 2:
                    roles.append(interaction.guild.get_role(int((await session.get(Config, ConfigKey.T2_ROLE_ID.name)).value)))
                    old_role = interaction.guild.get_role(int((await session.get(Config, ConfigKey.T1_ROLE_ID.name)).value))
                elif log.tier == 3 and (await session.execute(stmt)).scalar() + 1 >= 3:
                    roles.append(interaction.guild.get_role(int((await session.get(Config, ConfigKey.T3_ROLE_ID.name)).value)))
                    roles.append(interaction.guild.get_role(int((await session.get(Config, log.role.get_config_key().name)).value)))
                    old_role = interaction.guild.get_role(int((await session.get(Config, ConfigKey.T2_ROLE_ID.name)).value))

                if roles:
                    for role in roles:
                        await member.add_roles(role)
                        role_assignment_text += f"\nYou have been assigned {role.name} {get_random_success_emote()}"
                    await member.remove_roles(old_role)
                emote = get_random_success_emote()
            await ta_channel.send(content=f"{member.mention} {self.feedback} {emote}\n{role_assignment_text}")

            # Update application
            log.status = self.status
            log.reviewer = interaction.user.id

            # Cleanup
            await (await rr_channel.fetch_message(log.review_message_id)).delete()
            log.review_message_id = None
        self.parent_view.stop()
        await interaction.followup.send(content=f"The log has been {self.status}", ephemeral=True)

        # Log
        embed = Embed(title=f"Log review: {self.status}", colour=self.status.colour)
        embed.description = f"**ID:** {self.log_id}\n**User:** {member}\n**Reviewer:** {interaction.user.mention}\n"
        embed.add_field(name="Feedback", value=self.feedback)
        await log_to_channel(self.bot, embed)
