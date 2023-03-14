from typing import Optional
from sqlalchemy import ForeignKey, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base
from models.enums.profession import Profession


class Build(Base):
    __tablename__ = "builds"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    url: Mapped[Optional[str]]
    profession: Mapped[Profession]
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipment.id"), nullable=True)
    equipment = relationship("Equipment", foreign_keys=[equipment_id], lazy="joined", single_parent=True, cascade="all, delete, delete-orphan")

    def __str__(self):
        return f"{self.name}{' (' + self.url + ')' if self.url else ''}:\n{self.equipment}"

    async def get(self, profession: Profession, session: AsyncSession):
        stmt = select(Build).where(Build.profession == profession)
        result = await session.execute(stmt)
        instance = result.scalars().all()
        return instance
