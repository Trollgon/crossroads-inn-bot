from enum import Enum
from models.feedback import FeedbackLevel


class ApplicationStatus(Enum):
    ACCEPTED = 0
    DENIED = 1
    NO_REVIEW_REQUESTED = 2
    WAITING_FOR_REVIEW = 3
    REVIEW_ACCEPTED = 4
    REVIEW_DENIED = 5

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