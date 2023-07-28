from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from models.base import Base
from models.enums.config_key import ConfigKey
from models.feedback import FeedbackGroup, Feedback, FeedbackLevel


class Config(Base):
    __tablename__ = "config"

    key: Mapped[str] = mapped_column(primary_key=True)
    value: Mapped[str] = mapped_column(nullable=False)

    def __init__(self, key: ConfigKey, value: str):
        super(Config, self).__init__()
        self.key = key.name
        self.value = value

    @staticmethod
    async def init(session: AsyncSession):
        session.add(Config(ConfigKey.MIN_GW2_BUILD, "147894"))
        session.add(Config(ConfigKey.MAX_SQUAD_DOWNS, "9"))
        session.add(Config(ConfigKey.MAX_SQUAD_DEATHS, "2"))
        session.add(Config(ConfigKey.MAX_PLAYER_DOWNS, "2"))

        session.add(Config(ConfigKey.LOG_CHANNEL_ID, "1079378660437528576"))
        session.add(Config(ConfigKey.GEAR_REVIEW_CHANNEL_ID, "1088082355866058802"))
        session.add(Config(ConfigKey.LOG_REVIEW_CHANNEL_ID, "1088082355866058802"))
        session.add(Config(ConfigKey.TIER_ASSIGNMENT_CHANNEL_ID, "1088074442179104818"))

        session.add(Config(ConfigKey.T0_ROLE_ID, "1088864141340594217"))
        session.add(Config(ConfigKey.T1_ROLE_ID, "1072652111709491200"))
        session.add(Config(ConfigKey.T2_ROLE_ID, "1079888828514447410"))
        session.add(Config(ConfigKey.T3_ROLE_ID, "1079888894025269258"))
        session.add(Config(ConfigKey.POWER_DPS_ROLE_ID, "1133150361868316682"))
        session.add(Config(ConfigKey.CONDITION_DPS_ROLE_ID, "1133159967994691645"))
        session.add(Config(ConfigKey.HEAL_ROLE_ID, "1133160011586093167"))
        session.add(Config(ConfigKey.BOON_DPS_ROLE_ID, "1133159862604406804"))

    @staticmethod
    async def all(session: AsyncSession):
        return (await session.execute(select(Config))).scalars().all()

    @staticmethod
    async def to_dict(session: AsyncSession):
        configs = await Config.all(session)
        return {ConfigKey[config.key]: config.value for config in configs}

    @staticmethod
    async def get_value(session: AsyncSession, key: ConfigKey):
        return (await session.execute(select(Config).where(Config.key == key.name))).scalar().value

    @staticmethod
    async def check(session: AsyncSession) -> FeedbackGroup:
        fbg = FeedbackGroup("Config")
        configs = await Config.all(session)
        for key in ConfigKey:
            if key.name not in [config.key for config in configs]:
                fbg.add(Feedback(f"Missing config value for key: {key.name}", FeedbackLevel.ERROR))
        if fbg.level == FeedbackLevel.SUCCESS:
            fbg.add(Feedback("All config value are present", FeedbackLevel.SUCCESS))
        else:
            fbg.add(Feedback("Use `/config init` or `/config set` to set the required values.", FeedbackLevel.WARNING))
        return fbg