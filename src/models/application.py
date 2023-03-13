from sqlalchemy import ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base
from models.enums.application_status import ApplicationStatus


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    discord_user_id: Mapped[int]
    status: Mapped[ApplicationStatus]
    time_created: Mapped[DateTime] = mapped_column(server_default=func.now())
    account_name: Mapped[str]
    character_name: Mapped[str]
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipment.id"), nullable=True)
    equipment = relationship("Equipment", foreign_keys=[equipment_id], lazy="joined", single_parent=True, cascade="all, delete, delete-orphan")
