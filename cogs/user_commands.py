import discord
from discord import app_commands, Interaction, Embed
from discord.ext import commands
import typing
from gw2.api import API
from cogs.views.application import ApplicationView
from gw2.models.feedback import *
from gw2.models.equipment import get_equipment, Equipment
from gw2.snowcrows import get_builds

professions = typing.Literal[
    "Guardian", "Warrior", "Revenant",
    "Engineer", "Ranger", "Thief",
    "Elementalist", "Mesmer", "Necromancer"
]


class UserCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.guild_only
    @app_commands.command(name="register")
    async def register(self, interaction: Interaction, api_key: str, character: str):
        # Defer to prevent interaction timeout
        await interaction.response.defer(ephemeral=True)

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
            embed.colour = discord.Colour.red()
            embed.add_field(name=f"{FeedbackLevel.ERROR.emoji} Please fix these errors and apply again.", value="", inline=False)
            await interaction.followup.send(embed=embed)
        else:
            embed.colour = discord.Colour.green()
            msg = await interaction.followup.send(embed=embed)
            view = ApplicationView(self.bot, api, character, msg)
            await view.init()
            await interaction.edit_original_response(embed=embed, view=view)

    @app_commands.guild_only
    @app_commands.command(name="gear")
    async def gear(self, interaction: Interaction, api_key: str, character: str, template: int):
        # Defer to prevent interaction timeout
        await interaction.response.defer()

        api = API(api_key)
        equipment: Equipment = await get_equipment(api, character, template)

        await interaction.followup.send(embed=equipment.to_embed())

    @app_commands.guild_only
    @app_commands.command(name="builds")
    async def builds(self, interaction: Interaction, profession: typing.Optional[professions]):
        builds = get_builds(profession)
        embed = Embed(title="Builds")
        for profession in builds:
            value = ""
            for build in builds[profession]:
                value += f"[{build}](https://snowcrows.com{builds[profession][build]})\n"
            embed.add_field(name=profession, value=value)
        await interaction.response.send_message(embed=embed)