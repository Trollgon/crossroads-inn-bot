import os
import discord
from discord import app_commands, Interaction, Embed
from discord.ext import commands
import typing
from gw2.snowcrows import add_build, remove_build, get_builds
from cogs.views.application_overview import ApplicationOverview

professions = typing.Literal[
    "Guardian", "Warrior", "Revenant",
    "Engineer", "Ranger", "Thief",
    "Elementalist", "Mesmer", "Necromancer"
]


class AdminCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.guild_only
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.default_permissions(administrator=True)
    @app_commands.command(name="init")
    async def init(self, interaction: Interaction):
        # Stop old view if it exists
        for view in self.bot.persistent_views:
            if type(view) == ApplicationOverview:
                view.stop()

        embed = Embed(title="Tier Application Bot",
                      description="You can use this bot to apply for Tiers on this server. "
                                  f"Currently only supports {interaction.guild.get_role(int(os.getenv('T1_ROLE_ID'))).name}.",
                      colour=discord.Colour.from_rgb(99, 51, 4)
                      )
        embed.set_author(name=self.bot.user.display_name,
                         icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.add_field(name=" ", value="", inline=False)
        embed.add_field(name="How to use",
                        value="1. Press the button below to start the application process\n"
                              "2. Enter your API key and the name of the character that you want to apply with. "
                              "__The bot will not store your API key__\n"
                              "3. The bot will check your Mastery and how many bosses you have killed\n"
                              "4. Select your equipment template and the build you want to apply for\n"
                              "5. The bot will compare your equipment to the build you selected\n"
                              "6. If your gear is correct to bot will automatically grant you the role\n",
                        inline=False)
        embed.add_field(name=" ", value="", inline=False)
        embed.add_field(name="How to get your API key",
                        value="1. Open the [API Key Management](https://account.arena.net/applications) and log into your ArenaNet account.\n"
                              "2. Press `New Key`\n"
                              "3. Enter a name for the key\n"
                              "4. Select the `account`, `characters` and `progression` permission\n"
                              "5. Press `Create API Key`\n",
                        inline=False)
        await interaction.channel.send(view=ApplicationOverview(self.bot), embed=embed)
        await interaction.response.send_message("Embed initialized", ephemeral=True)

    @commands.command("sync")
    @commands.is_owner()
    async def sync(self, ctx: commands.Context, sync_global: typing.Optional[bool] = False) -> None:
        if sync_global:
            await self.bot.tree.sync()
            await ctx.send("Synced commands globally")
        else:
            self.bot.tree.copy_global_to(guild=ctx.guild)
            await self.bot.tree.sync(guild=ctx.guild)
            await ctx.send("Synced commands to this guild")

    @app_commands.guild_only
    @app_commands.default_permissions(manage_roles=True)
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.command(name="builds")
    async def builds(self, interaction: Interaction, profession: typing.Optional[professions]):
        builds = get_builds(profession)
        embed = Embed(title="Builds")
        for profession in builds:
            value = ""
            for build in builds[profession]:
                value += f"[{build}](https://snowcrows.com{builds[profession][build]})\n"
            embed.add_field(name=profession, value=value)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    build = app_commands.Group(name="build", description="Add and remove builds")

    @app_commands.guild_only
    @app_commands.default_permissions(manage_roles=True)
    @app_commands.checks.has_permissions(manage_roles=True)
    @build.command(name="add")
    async def build_add(self, interaction: Interaction, snowcrows_url: str):
        if not snowcrows_url.startswith("https://snowcrows.com"):
            await interaction.response.send_message("Invalid url", ephemeral=True)
            return

        await add_build(url=snowcrows_url.replace("https://snowcrows.com", ""))
        await interaction.response.send_message("Build was added", ephemeral=True)

    @app_commands.guild_only
    @app_commands.default_permissions(manage_roles=True)
    @app_commands.checks.has_permissions(manage_roles=True)
    @build.command(name="remove")
    async def build_remove(self, interaction: Interaction, snowcrows_url: str):
        if not snowcrows_url.startswith("https://snowcrows.com"):
            await interaction.response.send_message("Invalid url", ephemeral=True)
            return

        if remove_build(url=snowcrows_url.replace("https://snowcrows.com", "")):
            await interaction.response.send_message("Build was removed", ephemeral=True)
        else:
            await interaction.response.send_message("Build not found", ephemeral=True)

