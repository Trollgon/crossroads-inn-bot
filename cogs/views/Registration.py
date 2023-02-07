import discord
from discord import Interaction
from gw2.snowcrows import get_sc_builds, get_sc_equipment
from gw2.compare import *
from gw2.models.equipment import get_equipment
from gw2.models.feedback import *


class SimpleDropdown(discord.ui.Select):
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()


class RegistrationView(discord.ui.View):
    def __init__(self, api: API, character: str):
        super().__init__()
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
        # Defer to prevent timeouts
        await interaction.response.defer(thinking=True)

        # Disable buttons
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)

        reference_equipment = await get_sc_equipment(self.api, self.sc_build_select.values[0])
        player_equipment = await get_equipment(self.api, self.character, int(self.equipment_tabs_select.values[0]))

        embed = Embed(title="Gearcheck Feedback",
                      description=f"Comparing equipment tab {player_equipment.name} to {reference_equipment.name}")
        compare_armor(player_equipment, reference_equipment).to_embed(embed, False)
        compare_trinkets(player_equipment, reference_equipment).to_embed(embed, False)
        compare_weapons(player_equipment, reference_equipment).to_embed(embed, False)

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
