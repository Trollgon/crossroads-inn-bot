import datetime
from sqlalchemy import DateTime, BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from models.base import Base
from models.enums.log_status import LogStatus


class Log(Base):
    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    discord_user_id: Mapped[int] = mapped_column(BigInteger)
    tier: Mapped[int]
    log_url: Mapped[str]
    encounter_id: Mapped[int]
    fight_name: Mapped[str]
    is_cm: Mapped[bool]
    status: Mapped[LogStatus]
    review_message_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    reviewer: Mapped[int] = mapped_column(BigInteger, nullable=True)
    submitted_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))

    def __init__(self):
        super(Log, self).__init__()
        self.submitted_at = datetime.datetime.utcnow()