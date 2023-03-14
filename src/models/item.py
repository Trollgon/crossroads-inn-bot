from typing import Optional
from models.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from models.enums.equipment_slot import EquipmentSlot
from models.enums.rarity import Rarity
from models.feedback import FeedbackGroup, Feedback, FeedbackLevel


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

    def compare(self, other, fbg: FeedbackGroup = FeedbackGroup("Item comparison"), min_rarity: Rarity = Rarity("Exotic")) -> FeedbackGroup:
        if not self.type == other.type:
            raise Exception("Can not compare different item types")

        # Compare item stats
        if self.stats != other.stats:
            fbg.add(Feedback(f"Your {self.stats} {self.type} should be {other.stats.name}", FeedbackLevel.WARNING))

        # Check rarity
        if self.rarity < min_rarity:
            fbg.add(Feedback(f"Your {self.type} has to be at least {min_rarity}", FeedbackLevel.ERROR))

        # Check level
        if self.level < 80:
            fbg.add(Feedback(f"Your {self.type} has to be a level 80 item", FeedbackLevel.ERROR))
        return fbg