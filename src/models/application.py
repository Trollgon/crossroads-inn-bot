import datetime
from sqlalchemy import ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base
from models.enums.application_status import ApplicationStatus


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    discord_user_id: Mapped[int]
    status: Mapped[ApplicationStatus]
    review_message_id: Mapped[int] = mapped_column(nullable=True)
    reviewer: Mapped[int] = mapped_column(nullable=True)
    time_created: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))
    account_name: Mapped[str]
    character_name: Mapped[str]
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipment.id"), nullable=True)
    equipment = relationship("Equipment", foreign_keys=[equipment_id], lazy="joined", single_parent=True, cascade="all, delete, delete-orphan")
    build_id = mapped_column(ForeignKey("builds.id"))
    build = relationship("Build", foreign_keys=[build_id], lazy="joined")

    def __init__(self):
        super(Application, self).__init__()
        self.time_created = datetime.datetime.utcnow()