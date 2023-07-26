from sqlalchemy.orm import Mapped, mapped_column
from models.base import Base
from models.enums.mech_mode import MechMode


class Mech(Base):
    __tablename__ = "mechs"

    id: Mapped[int] = mapped_column(primary_key=True)
    encounter_id: Mapped[int]
    name: Mapped[str]
    max_amount: Mapped[int]
    mode: Mapped[MechMode]


    def __init__(self, encounter_id: int, name: str, max_amount: int, mode: MechMode):
        super(Mech, self).__init__()
        self.encounter_id = encounter_id
        self.name = name
        self.max_amount = max_amount
        self.mode = mode

    def __str__(self):
        return f"[{self.id}] {self.encounter_id}, {self.name}, {self.max_amount} ({self.mode})"