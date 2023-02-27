from discord import app_commands, Interaction, Embed
from discord.ext import commands
import typing
from gw2.snowcrows import add_build, remove_build
from cogs.views.application_overview import ApplicationOverview


class AdminCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command("prepare")
    @commands.is_owner()
    async def prepare(self, ctx: commands.Context):
        embed = Embed(title="Tier Application", description="Press button below to apply")
        await ctx.send(view=ApplicationOverview(self.bot), embed=embed)

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

        remove_build(url=snowcrows_url.replace("https://snowcrows.com", ""))
        await interaction.response.send_message("Build was removed", ephemeral=True)

