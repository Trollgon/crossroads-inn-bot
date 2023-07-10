from enum import Enum
import discord


class LogStatus(Enum):
    DENIED = 0
    WAITING_FOR_REVIEW = 1
    REVIEW_DENIED = 2
    REVIEW_ACCEPTED = 3

    def __str__(self):
        match self:
            case LogStatus.REVIEW_ACCEPTED:
                return "accepted"
            case LogStatus.DENIED | LogStatus.REVIEW_DENIED:
                return "denied"
            case LogStatus.WAITING_FOR_REVIEW:
                return "waiting for review"
    @property
    def colour(self) -> discord.Colour:
        match self:
            case LogStatus.REVIEW_ACCEPTED:
                return discord.Colour.green()
            case LogStatus.DENIED | LogStatus.REVIEW_DENIED:
                return discord.Colour.red()
            case _:
                return discord.Colour.yellow()