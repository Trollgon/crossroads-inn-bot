import datetime
from sqlalchemy import DateTime, BigInteger, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from models.base import Base
from models.boss import Boss
from models.enums.log_status import LogStatus
from models.enums.pools import BossLogPool


class Log(Base):
    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    discord_user_id: Mapped[int] = mapped_column(BigInteger)
    tier: Mapped[int]
    log_url: Mapped[str]
    encounter_id: Mapped[int]
    fight_name: Mapped[str]
    is_cm: Mapped[bool]
    assigned_pool: Mapped[BossLogPool]
    status: Mapped[LogStatus]
    review_message_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    reviewer: Mapped[int] = mapped_column(BigInteger, nullable=True)
    submitted_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))

    def __init__(self):
        super(Log, self).__init__()
        self.submitted_at = datetime.datetime.utcnow()

    async def assign_pool(self, session: AsyncSession):
        boss = (await session.execute(select(Boss).where(Boss.encounter_id == self.encounter_id).where(Boss.is_cm == self.is_cm))).scalar()
        if boss:
            self.assigned_pool = boss.log_pool
        elif self.is_cm:
            # If the log is a CM, but we don't have a CM boss, check for a non-CM boss
            boss = (await session.execute(select(Boss).where(Boss.encounter_id == self.encounter_id))).scalar()
            if boss:
                self.assigned_pool = boss.log_pool

        if not self.assigned_pool:
            self.assigned_pool = BossLogPool.NOT_ALLOWED