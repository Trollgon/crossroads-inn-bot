import os

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from models.base import Base


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


engine = create_async_engine(os.getenv("DATABASE_URL"), echo=False)
Session = async_sessionmaker(engine)
