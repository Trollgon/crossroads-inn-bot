from typing import Optional, List
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

    @property
    def upgrades(self) -> List[str]:
        upgrades = []
        for upgrade in [self.upgrade_1, self.upgrade_2]:
            if upgrade:
                upgrades.append(upgrade)
        return upgrades

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

    def compare(self, other, fbg: FeedbackGroup = FeedbackGroup("Item comparison")) -> FeedbackGroup:
        # Compare item stats
        if self.stats != other.stats:
            fbg.add(Feedback(f"Your {self.stats} {self.type} should be {other.stats}", FeedbackLevel.WARNING))

        # Check if upgrades exist
        if len(self.upgrades) < len(other.upgrades):
            # Legendary weapons sometimes show up without a sigil
            if self.rarity == Rarity.Legendary and self.slot in EquipmentSlot.get_weapon_slots():
                fbg.add(Feedback(f"Your {self.type} is missing a sigil. "
                                 f"This error gets ignored because legendary weapons sometimes show up without sigils",
                                 FeedbackLevel.SUCCESS))
            else:
                fbg.add(Feedback(f"Your {self.type} is missing a "
                                 f"{'sigil' if self.type in EquipmentSlot.get_weapon_slots() else ' rune'}. "
                                 f"It should have a {' and a '.join(f'{upgrade}' for upgrade in other.upgrades)}",
                                 FeedbackLevel.ERROR))
            return fbg

        # Compare upgrades. Order of upgrades doesn't matter
        upgrades_other = other.upgrades
        upgrades_self = self.upgrades
        for upgrade in other.upgrades:
            if upgrade in upgrades_self:
                upgrades_self.remove(upgrade)
                upgrades_other.remove(upgrade)

        if upgrades_other or upgrades_self:
            fbg.add(Feedback(f"Your {self.type} has a {' and '.join(f'{upgrade}' for upgrade in self.upgrades)}"
                             f" instead of a {' and '.join(f'{upgrade}' for upgrade in other.upgrades)}",
                             FeedbackLevel.WARNING))
        return fbg

    def check_basics(self, fbg: FeedbackGroup = FeedbackGroup("Basic item checks"),
                       min_rarity: Rarity = Rarity.Exotic, min_level: int = 80):
        # Check rarity
        if self.rarity < min_rarity:
            fbg.add(Feedback(f"Your {self.type} has to be at least {min_rarity}", FeedbackLevel.ERROR))

        # Check level
        if self.level < min_level:
            fbg.add(Feedback(f"Your {self.type} has to be a level {min_level} item", FeedbackLevel.ERROR))
        return fbg