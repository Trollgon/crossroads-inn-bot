import discord
from discord import Interaction
from gw2.snowcrows import get_sc_builds, get_sc_equipment
from gw2.compare import *
from gw2.models.equipment import get_equipment
from gw2.models.feedback import *
from discord.ext import commands


RR_CHANNEL_ID = 1072617994565455966
T1_ROLE_ID = 1072652111709491200


class SimpleDropdown(discord.ui.Select):
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()


class SimpleButtonView(discord.ui.View):
    def __init__(self, title, func, *args):
        super().__init__()
        self.func = func
        self.args = args
        self.children[0].label = title

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Disable button
        button.disabled = True
        await interaction.message.edit(view=self)
        self.stop()

        await self.func(interaction, *self.args)
        await interaction.response.send_message("The manual gearcheck has successfully been requested")


class RegistrationView(discord.ui.View):
    def __init__(self, bot: commands.Bot, api: API, character: str):
        super().__init__()
        self.bot = bot
        self.api = api
        self.character = character

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

        # Snowcrows build select
        for build in (await get_sc_builds(character_data["profession"])).items():
            self.sc_build_select.add_option(label=build[0], value=build[1])
        self.add_item(self.sc_build_select)

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=2, disabled=True)
    async def search(self, interaction: Interaction, button: discord.ui.Button):
        # Disable buttons so it cant be pressed twice
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)

        # Defer to prevent timeouts
        await interaction.response.defer(thinking=True)

        reference_equipment = await get_sc_equipment(self.api, self.sc_build_select.values[0])
        player_equipment = await get_equipment(self.api, self.character, int(self.equipment_tabs_select.values[0]))

        embed = Embed(title="Gearcheck Feedback",
                      description=f"Comparing equipment tab {player_equipment.name} to {reference_equipment.name}")
        fbc = FeedbackCollection()
        fbc.add(compare_armor(player_equipment, reference_equipment))
        fbc.add(compare_trinkets(player_equipment, reference_equipment))
        fbc.add(compare_weapons(player_equipment, reference_equipment))
        fbc.to_embed(embed, False)

        match fbc.level:
            case FeedbackLevel.SUCCESS:
                await interaction.guild.get_member(interaction.user.id).add_roles(interaction.guild.get_role(T1_ROLE_ID))
                embed.add_field(name=f"{FeedbackLevel.SUCCESS.emoji} Success! You are now Tier 1.", value="")
                await interaction.followup.send(embed=embed)

            case FeedbackLevel.WARNING:
                await interaction.followup.send(embed=embed, view=SimpleButtonView("Request Manual Review", request_equipment_review, player_equipment, self.bot))

            case FeedbackLevel.ERROR:
                embed.add_field(name=f"{FeedbackLevel.ERROR.emoji} Please fix all of the errors in your gear and try again.", value="")
                await interaction.followup.send(embed=embed)

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
            await interaction.message.edit(view=self)
        return True


async def request_equipment_review(interaction: Interaction, equipment: Equipment, bot: commands.Bot):
    embed = Embed(title="Equipment Review",
                  description=f"{interaction.user.mention} failed the automatic gear check and requested a manual review.")
    await bot.get_channel(RR_CHANNEL_ID).send(embed=equipment.to_embed(embed))