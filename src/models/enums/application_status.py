from enum import Enum
import discord
from models.feedback import FeedbackLevel


class ApplicationStatus(Enum):
    ACCEPTED = 0
    DENIED = 1
    NO_REVIEW_REQUESTED = 2
    WAITING_FOR_REVIEW = 3
    CLOSED_BY_APPLICANT = 4
    REVIEW_ACCEPTED = 5
    REVIEW_DENIED = 6

    @staticmethod
    def from_feedback(feedback: FeedbackLevel):
        match feedback:
            case FeedbackLevel.ERROR:
                return ApplicationStatus.DENIED
            case FeedbackLevel.SUCCESS:
                return ApplicationStatus.ACCEPTED
            case _:
                return ApplicationStatus.NO_REVIEW_REQUESTED

    def __str__(self):
        match self:
            case ApplicationStatus.ACCEPTED | ApplicationStatus.REVIEW_ACCEPTED:
                return "accepted"
            case ApplicationStatus.DENIED | ApplicationStatus.REVIEW_DENIED:
                return "denied"
            case ApplicationStatus.NO_REVIEW_REQUESTED:
                return "no review requested"
            case ApplicationStatus.WAITING_FOR_REVIEW:
                return "waiting for review"
            case ApplicationStatus.CLOSED_BY_APPLICANT:
                return "closed by applicant"

    @property
    def colour(self) -> discord.Colour:
        match self:
            case ApplicationStatus.ACCEPTED | ApplicationStatus.REVIEW_ACCEPTED:
                return discord.Colour.green()
            case ApplicationStatus.DENIED | ApplicationStatus.REVIEW_DENIED:
                return discord.Colour.red()
            case _:
                return discord.Colour.yellow()