from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    def __init__(self):
        print("creating base")
        super().__init__()
