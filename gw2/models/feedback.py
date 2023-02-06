from enum import Enum
from discord import Embed
from cogs.utils import split_embed


class FeedbackLevel(Enum):
    INFO = 1
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
    def __init__(self, message: str, level: FeedbackLevel = FeedbackLevel.INFO):
        self.message: str = message
        self.level: FeedbackLevel = level


class FeedbackCollection:
    def __init__(self, message: str):
        self.level: FeedbackLevel = FeedbackLevel.INFO
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