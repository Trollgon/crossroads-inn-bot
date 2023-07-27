import re
import aiohttp
from discord import app_commands, Interaction, Embed
from discord.ext import commands
from sqlalchemy import select, delete
from database import Session
from helpers.custom_embed import CustomEmbed
from helpers.embeds import split_embed
from helpers.log_checks import check_mechanics
from models.boss import Boss
from models.enums.mech_mode import MechMode
from models.feedback import FeedbackGroup
from models.mech import Mech


class MechCommands(commands.Cog):
    mech = app_commands.Group(name="mech", description="Configure mechanic checks for a boss.")

    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @app_commands.guild_only
    @app_commands.default_permissions(manage_roles=True)
    @app_commands.checks.has_permissions(manage_roles=True)
    @mech.command(name="help", description="Show help page")
    async def mech_help(self, interaction: Interaction):
        embed = CustomEmbed(self.bot, title="Mechanics Help")
        embed.description = "Mechanic checks can be used to instantly decline a log when a player/squad has failed it too many times." \
                            "You can use the following subcommands to configure the mechanic checks."
        embed.add_field(name="Subcommands",
                        value="- `/mech list [encounter_id]`: Show a list of all configured mechanics\n"
                              "- `/mech add: <encounter_id> <name> <max_amount> <mode>`: Add a mechanic check\n"
                              "- `/mech delete <id>`: Delete a mechanic check\n"
                              "- `/mech edit <id> [encounter_id] [name] [max_amount] [mode]`: Edit a mechanic check\n"
                              "- `/mech init`: Drop the table and initialize it with default mechanic checks\n",
                        inline=False)
        embed.add_field(name="Arguments",
                        value="- `encounter_id`: The encounter id of the boss. See `/boss list`\n"
                              "- `name`: The name of the mechanic. See dps.report `Mechanics` tab\n"
                              "- `max_amount`: The maximum amount of times the mechanic can be failed\n"
                              "- `mode`: The mode of the mechanic check:\n"
                              " - `PLAYER`: Only check for the player that submitted the log\n"
                              " - `SQUAD`: Check the sum of failures of all players in the squad\n",
                        inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)


    @app_commands.guild_only
    @app_commands.default_permissions(manage_roles=True)
    @app_commands.checks.has_permissions(manage_roles=True)
    @mech.command(name="list", description="List all mechanic checks.")
    async def mech_list(self, interaction: Interaction, encounter_id: int = None):
        stmt = select(Mech).order_by(Mech.encounter_id, Mech.id)
        if encounter_id:
            stmt = stmt.where(Mech.encounter_id == encounter_id)

        embed = CustomEmbed(self.bot ,title="Mechanics", description="[id] name: max_amount (mode)")
        async with Session.begin() as session:
            mechs = (await session.execute(stmt)).scalars()
            encounter_id = -1
            boss = None
            value = ""
            for mech in mechs:
                if mech.encounter_id != encounter_id:
                    if value != "":
                        split_embed(embed, f"{boss.boss_name} ({boss.encounter_id})", value, inline=True)
                        value = ""
                    boss = (await session.get(Boss, (mech.encounter_id, False)))
                    encounter_id = mech.encounter_id
                value += f"[{mech.id}] {mech.name}: {mech.max_amount} ({mech.mode})\n"
            split_embed(embed, f"{boss.boss_name} ({boss.encounter_id})", value, inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.guild_only
    @app_commands.default_permissions(manage_roles=True)
    @app_commands.checks.has_permissions(manage_roles=True)
    @mech.command(name="add", description="Add a mechanic check to a boss.")
    async def mech_add(self, interaction: Interaction, encounter_id: int, name: str, max_amount: int, mode: MechMode):
        async with Session.begin() as session:
            # Check if the mech already exists
            mech = (await session.execute(select(Mech).where(Mech.encounter_id == encounter_id).where(Mech.name == name))).scalar()
            if mech:
                await interaction.response.send_message(f"This mechanic already exists. Use `/mech edit id:{mech.id}`.", ephemeral=True)
                return

            # Check if the boss exists
            boss = (await session.execute(select(Boss).where(Boss.encounter_id == encounter_id))).scalar()
            if not boss:
                await interaction.response.send_message(f"This boss does not exist. Use `/boss list` to see all bosses.", ephemeral=True)
                return

            if max_amount < 0:
                await interaction.response.send_message(f"The max amount must be at least 0.", ephemeral=True)
                return

            # Create mech
            mech = Mech(encounter_id, name, max_amount, mode)
            session.add(mech)
            await session.flush()
            await session.refresh(mech)
            await interaction.response.send_message(f"Mechanic check was added:\n{str(mech)}", ephemeral=True)


    @app_commands.guild_only
    @app_commands.default_permissions(manage_roles=True)
    @app_commands.checks.has_permissions(manage_roles=True)
    @mech.command(name="delete", description="Delete a mechanic check.")
    async def mech_delete(self, interaction: Interaction, mech_id: int):
        async with Session.begin() as session:
            mech = (await session.execute(select(Mech).where(Mech.id == mech_id))).scalar()
            if not mech:
                await interaction.response.send_message(f"This mechanic does not exist. Use `/mech list` to see all mechanics.", ephemeral=True)
                return

            mech_str = str(mech)
            await session.delete(mech)
        await interaction.response.send_message(f"Mechanic check was deleted:\n{mech_str}", ephemeral=True)


    @app_commands.guild_only
    @app_commands.default_permissions(manage_roles=True)
    @app_commands.checks.has_permissions(manage_roles=True)
    @mech.command(name="edit", description="Edit a mechanic check.")
    async def mech_edit(self, interaction: Interaction, mech_id: int, encounter_id: int = None, name: str = None, max_amount: int = None, mode: MechMode = None):
        async with Session.begin() as session:
            mech = (await session.execute(select(Mech).where(Mech.id == mech_id))).scalar()
            if not mech:
                await interaction.response.send_message(f"This mechanic does not exist. Use `/mech list` to see all mechanics.", ephemeral=True)
                return

            if encounter_id:
                # Check if the boss exists
                boss = (await session.execute(select(Boss).where(Boss.encounter_id == encounter_id))).scalar()
                if not boss:
                    await interaction.response.send_message(f"This boss does not exist. Use `/boss list` to see all bosses.", ephemeral=True)
                    return
                mech.encounter_id = encounter_id

            if name:
                mech.name = name

            if max_amount:
                if max_amount < 0:
                    await interaction.response.send_message(f"The max amount must be at least 0.", ephemeral=True)
                    return
                mech.max_amount = max_amount

            if mode:
                mech.mode = mode

            await session.flush()
            await session.refresh(mech)
            await interaction.response.send_message(f"Mechanic check was edited:\n{str(mech)}", ephemeral=True)

    @app_commands.guild_only
    @app_commands.default_permissions(manage_roles=True)
    @app_commands.checks.has_permissions(manage_roles=True)
    @mech.command(name="init", description="Drop the table and initialize it with default mechanic checks.")
    async def mech_init(self, interaction: Interaction):
        async with Session.begin() as session:
            await session.execute(delete(Mech))
            Mech.init(session)
        await interaction.response.send_message(f"Mechanic checks were initialized.", ephemeral=True)


    @app_commands.guild_only
    @app_commands.default_permissions(manage_roles=True)
    @app_commands.checks.has_permissions(manage_roles=True)
    @mech.command(name="test", description="Test a mechanic check.")
    async def mech_test(self, interaction: Interaction, log_url: str, account_name: str, mech_id: int = None):
        await interaction.response.defer(thinking=True, ephemeral=True)

        # Check if log url is valid
        pattern = re.compile("https:\/\/dps\.report\/[a-zA-Z\-0-9\_]+")
        if not pattern.match(log_url):
            await interaction.followup.send(f"Invalid log url.", ephemeral=True)
            return

        # Get json data from dps.report
        error = ""
        async with aiohttp.ClientSession() as session:
            async with session.get("https://dps.report/getJson?permalink=" + log_url) as r:
                if r.status == 200:
                    try:
                        log_json = await r.json()
                    except Exception as e:
                        error = f"{log_url}\n{e}"
                else:
                    error = f"{log_url}\n{r.status}: {await r.text()}"

        if error:
            await interaction.followup.send(f"Error while parsing log:\n{error}", ephemeral=True)
            return

        # Check if mech exists for this boss
        async with Session.begin() as session:
            stmt = select(Mech).where(Mech.encounter_id == log_json["eiEncounterID"])
            if not (await session.execute(stmt)).scalars().all():
                await interaction.followup.send(f"No mechanics are configured for this boss. Use `/mech list` to see all mechanics.", ephemeral=True)
                return

            # Check if the mech exists
            if mech_id:
                mech = (await session.execute(stmt.where(Mech.id == mech_id))).scalar()
                if not mech:
                    await interaction.followup.send(f"This mechanic does not exist on this boss. Use `/mech list` to see all mechanics.", ephemeral=True)
                    return


        fbg = FeedbackGroup(message=f"Checking mechanics")
        await check_mechanics(log_json, account_name, fbg, mech_id, True)
        embed = fbg.to_embed(CustomEmbed(self.bot, title="Mechanic Test"))
        await interaction.followup.send(embed=embed, ephemeral=True)
