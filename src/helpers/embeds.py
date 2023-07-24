from typing import Dict
import discord
from discord import Embed
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from exceptions import APIException
from models.enums.log_status import LogStatus
from models.enums.role import Role
from models.log import Log


# Splits log text into multiple embed fields under one title
def split_embed(embed: Embed, title: str, text: str, inline: bool = False) -> Embed:
    text = text.splitlines(keepends=True)
    text_short = ""
    for line in text:
        if (len(text_short) + len(line)) <= 1024:
            text_short += line
        else:
            embed.add_field(name=title, value=text_short, inline=inline)
            text_short = line
            title = "\u200b"    # Invisible character to not repeat title

    if text_short != "":
        embed.add_field(name=title, value=text_short, inline=inline)

    return embed


def generate_error_embed(error: Exception):
    embed = Embed(title="Error", colour=discord.Colour.red())
    if isinstance(error, APIException):
        embed.description = f"**An error occurred while trying to access the Guild Wars 2 API:**\n" \
                            f"{error.error_message}"
    else:
        embed.description = "An unknown error occurred. Please try again later."
    return embed


async def get_progress_embed(session: AsyncSession, discord_user: discord.User) -> Embed:
    embed = discord.Embed(title="Tier Progress", color=discord.Color.green())
    embed.set_author(name=discord_user.display_name, icon_url=discord_user.avatar)
    stmt = select(Log).where(Log.discord_user_id == discord_user.id).where(Log.status != LogStatus.DENIED).order_by(desc(Log.status))

    # Tier 2
    logs = (await session.execute(stmt.where(Log.tier == 2))).scalars().all()

    value = ""
    accepted = 0
    for log in logs:
        value += f"[{log.fight_name}]({log.log_url}): {log.status}\n"
        accepted += 1 if log.status == LogStatus.REVIEW_ACCEPTED else 0
    embed.add_field(name=f"Tier 2:", value=f"Progress: {accepted}/2\n" + value, inline=False)

    # Tier 3
    for role in Role:
        if role == Role.NONE:
            continue
        logs = (await session.execute(stmt.where(Log.tier == 3).where(Log.role == role))).scalars().all()
        value = ""
        accepted = 0
        for log in logs:
            value += f"[{log.fight_name}]({log.log_url}): {log.status}\n"
            accepted += 1 if log.status == LogStatus.REVIEW_ACCEPTED else 0
        embed.add_field(name=f"Tier 3: {role.value}", value=f"Progress: {accepted}/3\n" + value, inline=False)

    return embed

def get_log_embed(log_url: str, log_json: Dict, discord_user: discord.User, account_name: str, role: Role, tier: int) -> Embed:
    embed = Embed(title=f"{log_json['fightName']}", colour=discord.Color.blurple(), url=log_url)
    embed.set_author(name=discord_user.display_name, icon_url=discord_user.avatar)
    embed.set_thumbnail(url=log_json["fightIcon"])
    embed.set_footer(text=f"eiEncounterID: {log_json['eiEncounterID']} | gW2Build: {log_json['gW2Build']}\n")
    for player in log_json["players"]:
        if player['account'] == account_name:
            profession = player['profession']
            break
    else:
        raise Exception(f"Could not find account {account_name} in log")

    embed.description = f"**Tier:** {tier}\n**Role:** {role.value}\n\n**Account:** {account_name}\n" \
                        f"**Profession:** {profession}\n**Duration:** {log_json['duration']}"
    return embed