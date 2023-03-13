from typing import Optional
from models.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from models.enums.equipment_slot import EquipmentSlot
from models.enums.rarity import Rarity


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    item_id: Mapped[int]
    name: Mapped[str]
    type: Mapped[str]
    level: Mapped[int]
    rarity: Mapped[Rarity]
    slot: Mapped[EquipmentSlot]
    stats: Mapped[str]
    upgrade_1: Mapped[Optional[str]]
    upgrade_2: Mapped[Optional[str]]

    def add_upgrade(self, upgrade: str):
        if not self.upgrade_1:
            self.upgrade_1 = upgrade
        elif not self.upgrade_2:
            self.upgrade_2 = upgrade
        else:
            raise Exception("Max amount of upgrades reached")

    def __str__(self):
        string = f"{self.rarity} {self.stats} {self.type}"
        if self.upgrade_1 and self.upgrade_2:
            string += f" ({self.upgrade_1}, {self.upgrade_2})"
        elif self.upgrade_1:
            string += f" ({self.upgrade_1})"
        return string
