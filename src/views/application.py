import os
from discord import Interaction
from api import API
from database import Session
from models.build import Build
from models.enums.profession import Profession
from models.equipment import Equipment
from models.feedback import *
from discord.ext import commands
from helpers.logging import log_gear_check
from helpers.embeds import generate_error_embed


class SimpleDropdown(discord.ui.Select):
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()


class SimpleButtonView(discord.ui.View):
    def __init__(self, title, original_message: discord.InteractionMessage, func, *args):
        super().__init__()
        self.original_message = original_message
        self.func = func
        self.args = args
        self.children[0].label = title

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Disable button
        button.disabled = True
        await self.original_message.edit(view=self)
        self.stop()

        await self.func(interaction, *self.args)
        await interaction.response.send_message(f"{FeedbackLevel.SUCCESS.emoji} The manual gearcheck was requested", ephemeral=True)

    async def on_error(self, interaction: Interaction, error: Exception, item: discord.ui.Item) -> None:
        await self.original_message.edit(content=None, view=None, embed=generate_error_embed(error))
        # Log error
        await super().on_error(interaction, error, item)


class ApplicationView(discord.ui.View):
    def __init__(self, bot: commands.Bot, api: API, character: str):
        super().__init__()
        self.bot = bot
        self.api = api
        self.character = character
        self.original_message = None

        self.equipment_tabs_select = SimpleDropdown(placeholder="Select your equipment template")
        self.build_select = SimpleDropdown(placeholder="Select your build")

    async def init(self):
        # Equipment template select
        character_data = await self.api.get_character_data(self.character)
        for equipment_tab in character_data["equipment_tabs"]:
            # Use equipment tab number if equipment tab name is empty (default)
            name = equipment_tab["name"] if equipment_tab["name"] else str(equipment_tab["tab"])
            self.equipment_tabs_select.add_option(label=name, value=str(equipment_tab["tab"]))
        self.add_item(self.equipment_tabs_select)

        # Build select
        async with Session() as session:
            builds = await Build.from_profession(session, Profession[character_data["profession"]])
        for build in builds:
            self.build_select.add_option(label=build.name, value=build.id)
        self.add_item(self.build_select)

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=2, disabled=True)
    async def submit(self, interaction: Interaction, button: discord.ui.Button):
        # Disable buttons so it cant be pressed twice
        for child in self.children:
            child.disabled = True
        await self.original_message.edit(view=self)

        # Defer to prevent timeouts
        await interaction.response.defer()
        async with Session() as session:
            build = await Build.find(session, id=int(self.build_select.values[0]))
        player_equipment = await self.api.get_equipment(self.character, int(self.equipment_tabs_select.values[0]))

        embed = Embed(title="Gearcheck Feedback",
                      description=f"**Comparing equipment tab {self.equipment_tabs_select.values[0]} to {build.to_link()}**\n"
                                  f"If your gear is not showing up correctly please equip the equipment template you selected\n\n"
                                  f"{FeedbackLevel.SUCCESS.emoji} **Success:** You have the correct gear\n"
                                  f"{FeedbackLevel.WARNING.emoji} **Warning:** Gear does not completely match the selected build\n"
                                  f"{FeedbackLevel.ERROR.emoji} **Error:** You need to fix these before you can apply\n")
        # Add additional whitespace for better separation
        embed.add_field(name=" ", value="", inline=False)

        fbc = player_equipment.compare(build.equipment)
        fbc.to_embed(embed, False)

        match fbc.level:
            case FeedbackLevel.SUCCESS:
                embed.colour = discord.Colour.green()
                await interaction.guild.get_member(interaction.user.id).add_roles(interaction.guild.get_role(int(os.getenv("T1_ROLE_ID"))))
                embed.add_field(name=f"{FeedbackLevel.SUCCESS.emoji} Success! You are now Tier 1.", value="")
                await self.original_message.edit(embed=embed, view=None)

            case FeedbackLevel.WARNING:
                embed.colour = discord.Colour.yellow()
                embed.add_field(name=f"{FeedbackLevel.WARNING.emoji} You did not pass the automatic gear check "
                                     f"but you can request a manual gear check. Use this if you are using a different "
                                     f"gear setup than Snowcrows.", value="")
                view = SimpleButtonView("Request Manual Review", self.original_message, request_equipment_review,
                                        player_equipment, self.bot, build.to_link())
                await self.original_message.edit(embed=embed, view=view)

            case FeedbackLevel.ERROR:
                embed.colour = discord.Colour.red()
                embed.add_field(name=f"{FeedbackLevel.ERROR.emoji} Please fix all of the errors in your gear and try again.", value="")
                await self.original_message.edit(embed=embed, view=None)

        await log_gear_check(self.bot, interaction, player_equipment, build, fbc)

    async def interaction_check(self, interaction: Interaction, /) -> bool:
        # Enable submit button if both selects have a value selected
        if self.equipment_tabs_select.values and self.build_select.values:
            self.children[0].disabled = False

            # Make sure options stay visually selected when updating view
            for opt in self.equipment_tabs_select.options:
                opt.default = opt.value in self.equipment_tabs_select.values
            for opt in self.build_select.options:
                opt.default = str(opt.value) in self.build_select.values
            # Update view
            await self.original_message.edit(view=self)
        return True

    async def on_error(self, interaction: Interaction, error: Exception, item: discord.ui.Item) -> None:
        await self.original_message.edit(content=None, view=None, embed=generate_error_embed(error))
        # Log error
        await super().on_error(interaction, error, item)


async def request_equipment_review(interaction: Interaction, equipment: Equipment, bot: commands.Bot, build: str):
    embed = Embed(title="Equipment Review",
                  description=f"{interaction.user.mention} failed the automatic gear check and requested a manual review.\n\n"
                              f"**Build:** {build}")
    await bot.get_channel(int(os.getenv("RR_CHANNEL_ID"))).send(embed=equipment.to_embed(embed))