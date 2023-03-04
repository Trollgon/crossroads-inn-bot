import discord
from discord import Embed
from exceptions import APIException


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