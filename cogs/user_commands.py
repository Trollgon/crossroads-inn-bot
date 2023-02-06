import discord
from discord import app_commands, Interaction, Embed
from discord.ext import commands
import typing
from gw2.api import API
from cogs.views.Registration import RegistrationView
from gw2.models.feedback import *

professions = typing.Literal[
    "Guardian", "Warrior", "Revenant",
    "Engineer", "Ranger", "Thief",
    "Elementalist", "Mesmer", "Necromancer"
]


class UserCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="register")
    async def register(self, interaction: Interaction, api_key: str, character: str):
        # Defer to prevent interaction timeout
        await interaction.response.defer()

        # Create embed
        embed = Embed(title="Application", color=0x0099ff)
        failed_registration = False

        # Check API Key
        api = API(api_key)
        key_feedback = await api.check_key()
        embed = key_feedback.to_embed(embed)
        if key_feedback.level == FeedbackLevel.ERROR:
            await interaction.followup.send(embed=embed)
            return

        if character in await api.get_characters():
            embed.add_field(name=f"{FeedbackLevel.SUCCESS.emoji} Character '{character}' found", value="", inline=False)
        else:
            embed.add_field(name=f"{FeedbackLevel.ERROR.emoji} Character '{character}' doesn't exist", value="", inline=False)
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
            embed.add_field(name=f"{FeedbackLevel.WARNING.emoji} Please fix these errors and apply again.", value="", inline=False)
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(embed=embed)
            view = RegistrationView(api, character)
            await view.init()
            await interaction.edit_original_response(embed=embed, view=view)


