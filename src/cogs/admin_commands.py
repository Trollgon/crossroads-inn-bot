import os
import discord
from discord import app_commands, Interaction, Embed
from discord.ext import commands
import typing
from sqlalchemy import select, func, desc
from database import Session
from models.application import Application
from models.build import Build
from models.enums.application_status import ApplicationStatus
from models.enums.profession import Profession
from models.feedback import FeedbackLevel
from snowcrows import get_sc_build, get_sc_builds
from views.application_overview import ApplicationOverview


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
    @app_commands.command(name="builds", description="Get a list of all allowed builds")
    async def builds(self, interaction: Interaction, profession: typing.Optional[Profession]):
        await interaction.response.defer(thinking=True, ephemeral=True)
        professions = []
        if profession:
            professions = [profession]
        else:
            for profession in Profession:
                professions.append(profession)

        embed = Embed(title="Builds")
        async with Session() as session:
            for profession in professions:
                value = ""
                for build in await Build.from_profession(session, profession):
                    value += f"{build.to_link()}\n"
                embed.add_field(name=profession.name, value=value)

        await interaction.followup.send(embed=embed, ephemeral=True)

    build = app_commands.Group(name="build", description="Add and remove builds")

    @app_commands.guild_only
    @app_commands.default_permissions(manage_roles=True)
    @app_commands.checks.has_permissions(manage_roles=True)
    @build.command(name="add", description="Add a build to the database")
    async def build_add(self, interaction: Interaction, snowcrows_url: str):
        if not snowcrows_url.startswith("https://snowcrows.com"):
            await interaction.response.send_message("Invalid url", ephemeral=True)
            return

        await interaction.response.defer(thinking=True, ephemeral=True)

        async with Session.begin() as session:
            if await Build.find(session, url=snowcrows_url):
                await interaction.followup.send("Build already exists", ephemeral=True)
                return
            build = await get_sc_build(snowcrows_url)
            session.add(build)
        await interaction.followup.send("Build was added", ephemeral=True)

    @app_commands.guild_only
    @app_commands.default_permissions(manage_roles=True)
    @app_commands.checks.has_permissions(manage_roles=True)
    @build.command(name="archive", description="Removes the build from the list of allowed builds")
    async def build_archive(self, interaction: Interaction, snowcrows_url: str):
        if not snowcrows_url.startswith("https://snowcrows.com"):
            await interaction.response.send_message("Invalid url", ephemeral=True)
            return

        async with Session.begin() as session:
            build = await Build.find(session, url=snowcrows_url)
            if build:
                build.archive()
                await interaction.response.send_message("Build was removed", ephemeral=True)
            else:
                await interaction.response.send_message("Build not found", ephemeral=True)

    @app_commands.guild_only
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    @build.command(name="init", description="Populates the database with all recommended and viable builds")
    async def build_init(self, interaction: Interaction):
        await interaction.response.defer(thinking=True, ephemeral=True)
        async with Session.begin() as session:
            for profession in Profession:
                urls = await get_sc_builds(profession)
                for url in urls:
                    build = await Build.find(session, url=url)
                    build_sc = await get_sc_build(url)
                    # If the build already exists in the DB: check if the gear is the same. if not archive old build
                    if build:
                        fbc = build.equipment.compare(build_sc.equipment)
                        if fbc.level <= FeedbackLevel.SUCCESS:
                            # Don't need to add it again if the gear is the same
                            continue
                        else:
                            build.archive()
                    session.add(build_sc)
        await interaction.followup.send("Added all recommended and viable builds (hand kite builds were ignored)", ephemeral=True)

    @app_commands.guild_only
    @app_commands.default_permissions(manage_roles=True)
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.command(name="stats", description="Show some stats about the applications")
    async def stats(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)

        embed = Embed(title="Application Stats")
        async with Session.begin() as session:
            # Total applications
            stmt = select(func.count(Application.id))
            res = await session.execute(stmt)
            embed.description = f"**Total applications:** {res.scalar()}"

            # Applications per status
            stmt = select(Application.status, func.count(Application.status)).group_by(Application.status)
            res = await session.execute(stmt)
            v = ""
            for r in res.all():
                v += f"{r.status.name}: {r.count}\n"
            embed.add_field(name="Applications per status:", value=v, inline=False)

            # Users with the most reviews
            stmt = select(Application.reviewer, func.count(Application.reviewer).label("count"))\
                .where(Application.status.in_((ApplicationStatus.REVIEW_ACCEPTED, ApplicationStatus.REVIEW_DENIED)))\
                .group_by(Application.reviewer).order_by(desc("count")).limit(5)
            res = await session.execute(stmt)
            v = ""
            for r in res.all():
                user = self.bot.get_user(r.reviewer)
                v += f"{user.mention if user else 'Unknown'}: {r.count}\n"
            embed.add_field(name="Most reviews:", value=v, inline=False)

            # Most popular accepted builds
            stmt = select(Build.name, func.count(Application.id).label("count")).join(Application)\
                .where(Application.status.in_((ApplicationStatus.REVIEW_ACCEPTED, ApplicationStatus.ACCEPTED)))\
                .group_by(Build.name).order_by(desc("count")).limit(10)
            res = await session.execute(stmt)
            v = ""
            for r in res.all():
                v += f"{r.name}: {r.count}\n"
            embed.add_field(name="Most popular accepted builds:", value=v, inline=False)
        await interaction.followup.send(embed=embed)
