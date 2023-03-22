from typing import Callable
import discord
from discord.ui import Button


class CallbackButton(Button):
    def __init__(self, callback: Callable, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._callback = callback

    async def callback(self, interaction: discord.Interaction):
        await self._callback(interaction)
