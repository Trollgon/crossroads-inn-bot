from sqlalchemy.ext.asyncio import AsyncSession
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
        self.name = name.strip()
        self.max_amount = max_amount
        self.mode = mode

    def __str__(self):
        return f"[{self.id}] {self.encounter_id}, {self.name}, {self.max_amount} ({self.mode})"

    @staticmethod
    def init(session: AsyncSession):
        # Gorseval
        session.add(Mech(131330, "Egg", 0, MechMode.PLAYER))
        session.add(Mech(131330, "Slam", 1, MechMode.PLAYER))

        # Slothasor
        session.add(Mech(131585, "Tantrum", 1, MechMode.PLAYER))

        # Keep Construct
        session.add(Mech(131842, "Jump", 1, MechMode.PLAYER))

        # Cairn
        session.add(Mech(132097, "KB", 1, MechMode.PLAYER))
        session.add(Mech(132097, "Port", 1, MechMode.PLAYER))

        # Samarog
        session.add(Mech(132099, "Schk.Wv", 1, MechMode.PLAYER))
        session.add(Mech(132099, "Swp", 1, MechMode.PLAYER))
        session.add(Mech(132099, "Slam", 1, MechMode.PLAYER))

        # Deimos
        session.add(Mech(132100, "Oil T.", 0, MechMode.PLAYER))
        session.add(Mech(132100, "Pizza", 1, MechMode.PLAYER))

        # Soulless Horror
        session.add(Mech(132353, "Slice1", 1, MechMode.PLAYER))
        session.add(Mech(132353, "Slice2", 1, MechMode.PLAYER))
        session.add(Mech(132353, "Golem", 1, MechMode.PLAYER))
        session.add(Mech(132353, "Scythe", 1, MechMode.PLAYER))

        # Dhuum
        session.add(Mech(132358, "Crack", 1, MechMode.PLAYER))
        session.add(Mech(132358, "Cone", 0, MechMode.PLAYER))

        # Twin Largos
        session.add(Mech(132610, "Float", 1, MechMode.PLAYER))
        session.add(Mech(132610, "Wave", 1, MechMode.PLAYER))

        # Qadim
        session.add(Mech(132611, "Q.Wave", 0, MechMode.PLAYER))
        session.add(Mech(132611, "Port", 1, MechMode.PLAYER))

        # Adina
        session.add(Mech(132865, "R.Blind", 1, MechMode.PLAYER))

        # Sabir
        session.add(Mech(132866, "Shockwave", 0, MechMode.PLAYER))
        session.add(Mech(132866, "Arena AoE", 1, MechMode.PLAYER))
