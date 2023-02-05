from discord import Embed


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
