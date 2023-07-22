import discord
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from models.base import Base
from models.enums.pools import *


class Boss(Base):
    __tablename__ = "bosses"

    ei_encounter_id: Mapped[int] = mapped_column(primary_key=True)
    is_cm: Mapped[bool] = mapped_column(primary_key=True)
    boss_name: Mapped[str]
    kp_pool: Mapped[KillProofPool]
    log_pool: Mapped[BossLogPool]
    achievement_id: Mapped[int] = mapped_column(nullable=True)

    def __init__(self,ei_encounter_id: int, is_cm: bool, boss_name: str, kp_pool: KillProofPool, log_pool: BossLogPool, achievement_id: int | None):
        super(Boss, self).__init__()
        self.ei_encounter_id = ei_encounter_id
        self.is_cm = is_cm
        self.boss_name = boss_name
        self.kp_pool = kp_pool
        self.log_pool = log_pool
        self.achievement_id = achievement_id

    @staticmethod
    async def init(session: AsyncSession):
        # Wing 1
        session.add(Boss(131329, False, "Vale Guardian", KillProofPool.POOL_B, BossLogPool.POOL_1, 2654))
        session.add(Boss(131330, False, "Gorseval", KillProofPool.POOL_A, BossLogPool.POOL_1, 2667))
        session.add(Boss(131331, False, "Sabetha", KillProofPool.POOL_B, BossLogPool.POOL_3, 2659))

        # Wing 2
        session.add(Boss(131585, False, "Slothasor", KillProofPool.POOL_B, BossLogPool.POOL_2, 2826))
        session.add(Boss(131586, False, "Bandit Trio", KillProofPool.NOT_ALLOWED, BossLogPool.NOT_ALLOWED, None))
        session.add(Boss(131587, False, "Matthias", KillProofPool.POOL_B, BossLogPool.POOL_3, 2836))

        # Wing 3
        session.add(Boss(131842, False, "Keep Construct", KillProofPool.POOL_B, BossLogPool.POOL_2, 3014))
        session.add(Boss(131843, False, "Twisted Castle", KillProofPool.NOT_ALLOWED, BossLogPool.NOT_ALLOWED, None))
        session.add(Boss(131844, False, "Xera", KillProofPool.POOL_B, BossLogPool.POOL_2, 3017))

        # Wing 4
        session.add(Boss(132097, False, "Cairn", KillProofPool.POOL_A, BossLogPool.POOL_1, 3349))
        session.add(Boss(132098, False, "Mursaat Overseer", KillProofPool.POOL_A, BossLogPool.NOT_ALLOWED, 3321))
        session.add(Boss(132099, False, "Samarog", KillProofPool.POOL_A, BossLogPool.POOL_1, 3347))
        session.add(Boss(132100, False, "Deimos", KillProofPool.POOL_B, BossLogPool.POOL_3, 3364))

        # Wing 5
        session.add(Boss(132353, False, "Soulless Horror", KillProofPool.POOL_B, BossLogPool.POOL_4, 4004))
        session.add(Boss(132354, False, "River of Souls", KillProofPool.NOT_ALLOWED, BossLogPool.NOT_ALLOWED, None))
        session.add(Boss(132355, False, "Statue of Ice", KillProofPool.NOT_ALLOWED, BossLogPool.NOT_ALLOWED, 4038))
        session.add(Boss(132356, False, "Statue of Death", KillProofPool.NOT_ALLOWED, BossLogPool.NOT_ALLOWED, 3998))
        session.add(Boss(132357, False, "Statue of Darkness", KillProofPool.NOT_ALLOWED, BossLogPool.NOT_ALLOWED, 4036))
        session.add(Boss(132358, False, "Dhuum", KillProofPool.POOL_B, BossLogPool.POOL_4, 4016))

        # Wing 6
        session.add(Boss(132609, False, "Conjured Amalgamate", KillProofPool.POOL_B, BossLogPool.POOL_2, 4423))
        session.add(Boss(132610, False, "Twin Largos", KillProofPool.POOL_B, BossLogPool.POOL_3, 4364))
        session.add(Boss(132611, False, "Qadim", KillProofPool.POOL_B, BossLogPool.POOL_4, 4396))

        # Wing 7
        session.add(Boss(132865, False, "Cardinal Adina", KillProofPool.POOL_B, BossLogPool.POOL_2, 4796))
        session.add(Boss(132866, False, "Cardinal Sabir", KillProofPool.POOL_B, BossLogPool.POOL_3, 4801))
        session.add(Boss(132867, False, "Qadim the Peerless", KillProofPool.POOL_B, BossLogPool.POOL_4, 4799))

        # IBS Strike Missions
        session.add(Boss(262661, False, "Whisper of Jormag", KillProofPool.POOL_A, BossLogPool.NOT_ALLOWED, 5118))

        # Eod Strike Missions
        session.add(Boss(262913, False, "Mai Trin", KillProofPool.NOT_ALLOWED, BossLogPool.NOT_ALLOWED, None))
        session.add(Boss(262914, False, "Ankka", KillProofPool.NOT_ALLOWED, BossLogPool.NOT_ALLOWED, None))
        session.add(Boss(262915, False, "Kaineng Overlook", KillProofPool.POOL_A, BossLogPool.NOT_ALLOWED, 6243))
        session.add(Boss(262916, False, "Harvest Temple", KillProofPool.POOL_A, BossLogPool.NOT_ALLOWED, 6513))

        # Eod Strike Mission CMs
        session.add(Boss(262913, True, "Mai Trin", KillProofPool.POOL_B, BossLogPool.POOL_1, 6433))
        session.add(Boss(262914, True, "Ankka", KillProofPool.POOL_A, BossLogPool.POOL_1, 6411))
        session.add(Boss(262915, True, "Kaineng Overlook", KillProofPool.POOL_B, BossLogPool.POOL_4, 6431))
        session.add(Boss(262916, True, "Harvest Temple", KillProofPool.POOL_B, BossLogPool.POOL_4, 6115))

        await session.commit()

    @staticmethod
    async def all(session: AsyncSession):
        return (await session.execute(select(Boss))).scalars().all()

    @staticmethod
    async def get(session: AsyncSession, ei_encounter_id: int, is_cm: bool):
        return await session.get(Boss, (ei_encounter_id, is_cm))

    def to_csv(self):
        return f"{self.ei_encounter_id}, " \
               f"{self.boss_name}, " \
               f"{self.is_cm}, " \
               f"{self.kp_pool.value}, " \
               f"{self.log_pool.value}, " \
               f"{self.achievement_id}"

    def __str__(self):
        return f"Boss(ei_encounter_id={self.ei_encounter_id}, " \
               f"is_cm={self.is_cm}, " \
               f"boss_name={self.boss_name}, " \
               f"kp_pool={self.kp_pool}, " \
               f"log_pool={self.log_pool}, " \
               f"achievement_id={self.achievement_id})"
