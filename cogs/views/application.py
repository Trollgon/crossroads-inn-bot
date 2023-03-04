import discord
from discord import Interaction
from gw2.snowcrows import get_sc_equipment, get_builds
from gw2.compare import *
from gw2.models.equipment import get_equipment
from gw2.models.feedback import *
from discord.ext import commands
from config import *
from cogs.logging import log_gear_check


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
        # Send message to user and log error
        await interaction.response.send_message(ephemeral=True, content="An unknown error occured. Please try again later.")
        await super().on_error(interaction, error, item)


class ApplicationView(discord.ui.View):
    def __init__(self, bot: commands.Bot, api: API, character: str, original_message: discord.InteractionMessage):
        super().__init__()
        self.bot = bot
        self.api = api
        self.character = character
        self.original_message = original_message

        self.equipment_tabs_select = SimpleDropdown(placeholder="Select your equipment template")
        self.sc_build_select = SimpleDropdown(placeholder="Select your build")

    async def init(self):
        # Equipment template select
        character_data = await self.api.get_character_data(self.character)
        for equipment_tab in character_data["equipment_tabs"]:
            # Use equipment tab number if equipment tab name is empty (default)
            name = equipment_tab["name"] if equipment_tab["name"] else str(equipment_tab["tab"])
            self.equipment_tabs_select.add_option(label=name, value=str(equipment_tab["tab"]))
        self.add_item(self.equipment_tabs_select)

        # Build select
        builds = get_builds(character_data["profession"])[character_data["profession"]]
        for build in builds:
            self.sc_build_select.add_option(label=build, value=builds[build])
        self.add_item(self.sc_build_select)

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=2, disabled=True)
    async def submit(self, interaction: Interaction, button: discord.ui.Button):
        # Disable buttons so it cant be pressed twice
        for child in self.children:
            child.disabled = True
        await self.original_message.edit(view=self)

        # Defer to prevent timeouts
        await interaction.response.defer()

        reference_equipment = await get_sc_equipment(self.api, self.sc_build_select.values[0])
        player_equipment = await get_equipment(self.api, self.character, int(self.equipment_tabs_select.values[0]))

        embed = Embed(title="Gearcheck Feedback",
                      description=f"**Comparing equipment tab {player_equipment.name} to {reference_equipment.name}**\n"
                                  f"If your gear is not showing up correctly please equip the equipment template you selected\n\n"
                                  f"{FeedbackLevel.SUCCESS.emoji} **Success:** You have the correct gear\n"
                                  f"{FeedbackLevel.WARNING.emoji} **Warning:** Gear does not completely match the selected build\n"
                                  f"{FeedbackLevel.ERROR.emoji} **Error:** You need to fix these before you can apply\n")
        # Add additional whitespace for better separation
        embed.add_field(name=" ", value="", inline=False)

        fbc = FeedbackCollection()
        fbc.add(compare_armor(player_equipment, reference_equipment))
        fbc.add(compare_trinkets(player_equipment, reference_equipment))
        fbc.add(compare_weapons(player_equipment, reference_equipment))
        fbc.to_embed(embed, False)

        match fbc.level:
            case FeedbackLevel.SUCCESS:
                embed.colour = discord.Colour.green()
                await interaction.guild.get_member(interaction.user.id).add_roles(interaction.guild.get_role(T1_ROLE_ID))
                embed.add_field(name=f"{FeedbackLevel.SUCCESS.emoji} Success! You are now Tier 1.", value="")
                await self.original_message.edit(embed=embed, view=None)

            case FeedbackLevel.WARNING:
                embed.colour = discord.Colour.yellow()
                embed.add_field(name=f"{FeedbackLevel.WARNING.emoji} You did not pass the automatic gear check "
                                     f"but you can request a manual gear check. Use this if you are using a different "
                                     f"gear setup than Snowcrows.", value="")
                view = SimpleButtonView("Request Manual Review", self.original_message, request_equipment_review,
                                        player_equipment, self.bot, reference_equipment.name)
                await self.original_message.edit(embed=embed, view=view)

            case FeedbackLevel.ERROR:
                embed.colour = discord.Colour.red()
                embed.add_field(name=f"{FeedbackLevel.ERROR.emoji} Please fix all of the errors in your gear and try again.", value="")
                await self.original_message.edit(embed=embed, view=None)

        await log_gear_check(self.bot, interaction, player_equipment, reference_equipment, fbc)

    async def interaction_check(self, interaction: Interaction, /) -> bool:
        # Enable submit button if both selects have a value selected
        if self.equipment_tabs_select.values and self.sc_build_select.values:
            self.children[0].disabled = False

            # Make sure options stay visually selected when updating view
            for opt in self.equipment_tabs_select.options:
                opt.default = opt.value in self.equipment_tabs_select.values
            for opt in self.sc_build_select.options:
                opt.default = opt.value in self.sc_build_select.values
            # Update view
            await self.original_message.edit(view=self)
        return True

    async def on_error(self, interaction: Interaction, error: Exception, item: discord.ui.Item) -> None:
        # Send message to user and log error
        await self.original_message.edit(content="An unknown error occured. Please try again later.")
        await super().on_error(interaction, error, item)


async def request_equipment_review(interaction: Interaction, equipment: Equipment, bot: commands.Bot, build: str):
    embed = Embed(title="Equipment Review",
                  description=f"{interaction.user.mention} failed the automatic gear check and requested a manual review.\n\n"
                              f"**Build:** {build}")
    await bot.get_channel(RR_CHANNEL_ID).send(embed=equipment.to_embed(embed))