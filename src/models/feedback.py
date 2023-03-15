from enum import Enum
import discord
from discord import Embed
from helpers.embeds import split_embed


class FeedbackLevel(Enum):
    SUCCESS = 1
    WARNING = 2
    ERROR = 3

    @property
    def emoji(self) -> str:
        match self.value:
            case 1:
                return ":white_check_mark:"
            case 2:
                return ":warning:"
            case 3:
                return ":x:"

    @property
    def colour(self) -> discord.Colour:
        match self.value:
            case 1:
                return discord.Colour.green()
            case 2:
                return discord.Colour.yellow()
            case 3:
                return discord.Colour.red()

    def __lt__(self, other):
        if self.value < other.value:
            return True
        return False

    def __le__(self, other):
        if self.value <= other.value:
            return True
        return False

    def __eq__(self, other):
        if self.value == other.value:
            return True
        return False

    def __ge__(self, other):
        if self.value >= other.value:
            return True
        return False

    def __gt__(self, other):
        if self.value > other.value:
            return True
        return False


class Feedback:
    def __init__(self, message: str, level: FeedbackLevel = FeedbackLevel.SUCCESS):
        self.message: str = message
        self.level: FeedbackLevel = level


class FeedbackGroup:
    def __init__(self, message: str):
        self.level: FeedbackLevel = FeedbackLevel.SUCCESS
        self.feedback: list[Feedback] = []
        self.message: str = message

    def add(self, feedback: Feedback) -> None:
        self.feedback.append(feedback)
        if feedback.level.value > self.level.value:
            self.level = feedback.level

    def to_embed(self, embed: Embed = Embed(title="Feedback"), inline: bool = False) -> Embed:
        value = ""
        for fb in self.feedback:
            value += f"{fb.level.emoji} {fb.message}\n"
        return split_embed(embed, f"{self.level.emoji} {self.message}:", value, inline)


class FeedbackCollection:
    def __init__(self):
        self.level: FeedbackLevel = FeedbackLevel.SUCCESS
        self.feedback: list[FeedbackGroup] = []

    def add(self, feedback_group: FeedbackGroup) -> None:
        self.feedback.append(feedback_group)
        if feedback_group.level.value > self.level.value:
            self.level = feedback_group.level

    def to_embed(self, embed: Embed = Embed(title="Feedback"), inline: bool = False) -> Embed:
        for fb in self.feedback:
            fb.to_embed(embed, inline)
            if not inline:
                # Add additional whitespace for better separation
                embed.add_field(name=" ", value="", inline=False)
        return embed
