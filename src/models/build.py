from typing import Optional
from sqlalchemy import ForeignKey, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base
from models.enums.profession import Profession


class Build(Base):
    __tablename__ = "builds"

    id: Mapped[int] = mapped_column(primary_key=True)
    archived: Mapped[bool] = mapped_column(default=False)
    name: Mapped[str]
    url: Mapped[Optional[str]]
    profession: Mapped[Profession]
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipment.id"), nullable=True)
    equipment = relationship("Equipment", foreign_keys=[equipment_id], lazy="joined", single_parent=True, cascade="all, delete, delete-orphan")

    def __str__(self):
        return f"{self.name}{' (' + self.url + ')' if self.url else ''}:\n{self.equipment}"

    def to_link(self):
        return f"[{self.name}]{'(' + self.url + ')' if self.url else ''}"

    @staticmethod
    async def from_profession(session: AsyncSession, profession: Profession, *, archived: bool = False):
        stmt = select(Build).where(Build.profession == profession).where(Build.archived == archived)
        result = await session.execute(stmt)
        instance = result.scalars().all()
        return instance

    @staticmethod
    async def find(session: AsyncSession, *, id: int = None, url: str = None, archived: bool = False):
        stmt = select(Build).where(Build.archived == archived)
        if id:
            stmt = stmt.where(Build.id == id)
        if url:
            stmt = stmt.where(Build.url == url)
        result = await session.execute(stmt)
        instance = result.scalar()
        return instance

    async def archive(self):
        self.archived = True