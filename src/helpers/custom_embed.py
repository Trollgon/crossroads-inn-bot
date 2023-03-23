import discord
from discord import Embed
from discord.ext.commands import Bot


class CustomEmbed(Embed):
    def __init__(self, bot: Bot, **kwargs):
        super().__init__(**kwargs)
        if not self.colour:
            self.colour = discord.Colour.from_rgb(99, 51, 4)
        self.set_author(name=bot.user.display_name, icon_url=bot.user.avatar.url if bot.user.avatar else None)