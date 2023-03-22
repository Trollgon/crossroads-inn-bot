import os
from discord import Interaction
from sqlalchemy import select

from database import Session
from helpers.embeds import generate_error_embed
from models.application import Application
from models.enums.application_status import ApplicationStatus
from models.feedback import *
from api import API
from views.application import ApplicationView
from discord.ext import commands


class ApplicationOverview(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label='Apply Tier 1', style=discord.ButtonStyle.primary, custom_id='persistent_view:t1')
    async def apply_t1(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user already has role
        for role in interaction.user.roles:
            if role.id in [int(os.getenv("T1_ROLE_ID")), int(os.getenv("T2_ROLE_ID")), int(os.getenv("T3_ROLE_ID"))]:
                await interaction.response.send_message(ephemeral=True, content="You are already Tier 1 or above.")
                return
        # Check if user already has an open application
        async with Session.begin() as session:
            stmt = select(Application).where(Application.discord_user_id == interaction.user.id)\
                .where(Application.status == ApplicationStatus.WAITING_FOR_REVIEW)
            res = (await session.execute(stmt)).scalar()
            if res:
                await interaction.response.send_message(ephemeral=True, content="You already have an open application. "
                                                                                "Please wait until it has been reviewed.")
                return
        await interaction.response.send_modal(ApplicationModal(self.bot))

    async def on_error(self, interaction: Interaction, error: Exception, item: discord.ui.Item) -> None:
        # Send message to user and log error
        await interaction.response.send_message(ephemeral=True, content="An unknown error occured. Please try again later.")
        await super().on_error(interaction, error, item)


class ApplicationModal(discord.ui.Modal, title="Tier 1 Application"):
    api_key: str = discord.ui.TextInput(label="API Key")
    character: str = discord.ui.TextInput(label="Character Name", min_length=3, max_length=19)

    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: Interaction) -> None:
        # Defer to prevent interaction timeout
        await interaction.response.defer(ephemeral=True, thinking=True)

        # Create embed
        embed = Embed(title="Tier 1 Application", color=0x0099ff)
        failed_registration = False

        # Check API Key
        api = API(str(self.api_key))
        key_feedback = await api.check_key()
        embed = key_feedback.to_embed(embed)
        if key_feedback.level == FeedbackLevel.ERROR:
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        if str(self.character) in await api.get_characters():
            embed.add_field(name=f"{FeedbackLevel.SUCCESS.emoji} Character '{self.character}' found", value="",
                            inline=False)
        else:
            embed.add_field(name=f"{FeedbackLevel.ERROR.emoji} Character '{self.character}' doesn't exist", value="",
                            inline=False)
            failed_registration = True

        # Check masteries
        mastery_feedback = await api.check_mastery()
        embed = mastery_feedback.to_embed(embed)
        if mastery_feedback.level == FeedbackLevel.ERROR:
            failed_registration = True

        # Check KP
        kp_feedback = await api.check_kp()
        embed = kp_feedback.to_embed(embed)
        if kp_feedback.level == FeedbackLevel.ERROR:
            failed_registration = True

        if failed_registration:
            embed.colour = discord.Colour.red()
            embed.add_field(name=f"{FeedbackLevel.ERROR.emoji} Please fix these errors and apply again.", value="",
                            inline=False)
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            embed.colour = discord.Colour.green()
            view = ApplicationView(self.bot, api, str(self.character))
            await view.init()
            response = await interaction.followup.send(embed=embed, ephemeral=True, view=view)
            view.original_message = response

    async def on_error(self, interaction: Interaction, error: Exception) -> None:
        await interaction.followup.send(embed=generate_error_embed(error), ephemeral=True)
        # Log error
        await super().on_error(interaction, error)