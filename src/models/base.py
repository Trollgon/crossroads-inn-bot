from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    def __init__(self):
        super().__init__()
