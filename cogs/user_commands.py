import discord
from discord import app_commands, Interaction, Embed
from discord.ext import commands
import typing
from gw2.api import API
from cogs.views.Registration import RegistrationView

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

        api = API(api_key)
        if await api.check_key():
            embed.add_field(name=":white_check_mark: API-Key valid", value="", inline=False)
        else:
            embed.add_field(name=":x: API-Key is not valid", value="", inline=False)
            await interaction.followup.send(embed=embed)
            return

        if character in await api.get_characters():
            embed.add_field(name=f":white_check_mark: Character '{character}' found", value="", inline=False)
        else:
            embed.add_field(name=f":x: Character '{character}' doesn't exist", value="", inline=False)
            failed_registration = True

        if await api.check_mastery():
            embed.add_field(name=":white_check_mark: Required Masteries are unlocked", value="", inline=False)
        else:
            embed.add_field(name=":x: Missing Masteries", value="", inline=False)
            failed_registration = True

        if await api.check_kp():
            embed.add_field(name=":white_check_mark: Reached required KP", value="", inline=False)
        else:
            embed.add_field(name=":x: Missing KP", value="", inline=False)
            failed_registration = True

        if failed_registration:
            embed.add_field(name=":exclamation: Please fix these errors and apply again.", value="", inline=False)
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(embed=embed)
            view = RegistrationView(api, character)
            await view.init()
            await interaction.edit_original_response(embed=embed, view=view)


