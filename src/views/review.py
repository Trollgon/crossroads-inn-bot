import os
import random
import discord
from discord import Interaction, ButtonStyle, Embed
from discord.ext import commands
from discord.ui import View, Modal
from database import Session
from models.application import Application
from models.enums.application_status import ApplicationStatus
from views.callback_button import CallbackButton
from helpers.logging import log_to_channel


class ReviewView(View):
    def __init__(self, bot: commands.Bot, application_id: int):
        super().__init__(timeout=None)
        self.bot = bot
        self.application_id = application_id
        self.add_item(CallbackButton(self.accept, label="Accept", style=ButtonStyle.green,
                                     custom_id=f"{self.bot.user.id}-application-{application_id}:accept"))
        self.add_item(CallbackButton(self.deny, label="Deny", style=ButtonStyle.red,
                                     custom_id=f"{self.bot.user.id}-application-{application_id}:deny"))

    async def accept(self, interaction: Interaction):
        await interaction.response.send_modal(ReviewModal(self.bot, ApplicationStatus.REVIEW_ACCEPTED, self.application_id, self))

    async def deny(self, interaction: Interaction):
        await interaction.response.send_modal(ReviewModal(self.bot, ApplicationStatus.REVIEW_DENIED, self.application_id, self))

    async def on_error(self, interaction: Interaction, error: Exception, item: discord.ui.Item) -> None:
        # Send message to user and log error
        await interaction.response.send_message(ephemeral=True, content="An unknown error occured. Please try again later.")
        await super().on_error(interaction, error, item)


emotes = ["<:feelsgoodman:312673949085335553>", "<:peeponice:729025840385359992>", "<:peeposmart:714504027332804679>",
          "<:peepoyes:621652180419608586>", "<:pepeglad:761608459732123655>", "<:jbcheer:941330593927532594>",
          "<:jbhappy:941330594397290526>", "<:jbheart:941330594258890842>", "<:jbhype:941330594279866388>"]


class ReviewModal(Modal, title="Tier 1 Application"):
    feedback = discord.ui.TextInput(label="Feedback", style=discord.TextStyle.paragraph)

    def __init__(self, bot: commands.Bot, status: ApplicationStatus, application_id: int, parent_view: View):
        self.bot = bot
        self.application_id = application_id
        self.parent_view = parent_view
        self.status = status

        match status:
            case ApplicationStatus.REVIEW_ACCEPTED:
                self.feedback.default = "Congrats on tier1"
            case ApplicationStatus.REVIEW_DENIED:
                self.feedback.default = "Your tier1 application has been denied"

        super().__init__()

    async def on_submit(self, interaction: Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        async with Session.begin() as session:
            application: Application = await session.get(Application, self.application_id)
            # Make sure application has not been handled already
            if application.status != ApplicationStatus.WAITING_FOR_REVIEW:
                reviewer = self.bot.get_user(application.reviewer)
                await interaction.followup.send(content=f"This application has already been {application.status} by {reviewer}", ephemeral=True)
                return

            # Add role and send feedback message
            emote = ""
            ta_channel = interaction.guild.get_channel(int(os.getenv("TIER_ASSIGNMENT_CHANNEL_ID")))
            rr_channel = interaction.guild.get_channel(int(os.getenv("RR_CHANNEL_ID")))
            member = interaction.guild.get_member(interaction.user.id)
            if self.status == ApplicationStatus.REVIEW_ACCEPTED:
                role = interaction.guild.get_role(int(os.getenv("T1_ROLE_ID")))
                emote = random.choice(emotes)
                await member.add_roles(role)
            await ta_channel.send(content=f"{member.mention} {self.feedback} {emote}")

            # Update application
            application.status = self.status
            application.reviewer = interaction.user.id
            await session.commit()

            # Cleanup
            await (await rr_channel.fetch_message(application.review_message_id)).delete()
            application.review_message_id = None
            self.parent_view.stop()
            await interaction.followup.send(content=f"The application has been {application.status}", ephemeral=True)

            # Log
            embed = Embed(title=f"Manual Gear Check: {application.status}", colour=application.status.colour)
            embed.description = f"**ID:** {application.id}\n**User:** {member.mention}\n**Reviewer:** {interaction.user.mention}\n"
            embed.add_field(name="Feedback", value=self.feedback)
            await log_to_channel(self.bot, embed)
