from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from models.base import Base
from models.enums.config_key import ConfigKey


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


    @staticmethod
    async def all(session: AsyncSession):
        return (await session.execute(select(Config))).scalars().all()

    @staticmethod
    async def to_dict(session: AsyncSession):
        configs = await Config.all(session)
        return {ConfigKey[config.key]: config.value for config in configs}