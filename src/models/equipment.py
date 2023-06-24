from copy import deepcopy
from typing import List
from sqlalchemy import ForeignKey
from discord import Embed
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base
from models.enums.equipment_slot import EquipmentSlot
from models.enums.rarity import Rarity
from models.feedback import FeedbackCollection, FeedbackGroup, Feedback, FeedbackLevel


class Equipment(Base):
    __tablename__ = "equipment"

    id: Mapped[int] = mapped_column(primary_key=True)
    stats_id = mapped_column(ForeignKey("equipment_stats.id"), nullable=True)
    stats = relationship("EquipmentStats", foreign_keys=[stats_id], lazy="joined", single_parent=True, cascade="all, delete, delete-orphan")

    # Armor
    helm_id: Mapped[int] = mapped_column(ForeignKey("items.id"), nullable=True)
    helm = relationship("Item", foreign_keys=[helm_id], lazy="joined", single_parent=True, cascade="all, delete, delete-orphan")
    shoulders_id: Mapped[int] = mapped_column(ForeignKey("items.id"), nullable=True)
    shoulders = relationship("Item", foreign_keys=[shoulders_id], lazy="joined", single_parent=True, cascade="all, delete, delete-orphan")
    coat_id: Mapped[int] = mapped_column(ForeignKey("items.id"), nullable=True)
    coat = relationship("Item", foreign_keys=[coat_id], lazy="joined", single_parent=True, cascade="all, delete, delete-orphan")
    gloves_id: Mapped[int] = mapped_column(ForeignKey("items.id"), nullable=True)
    gloves = relationship("Item", foreign_keys=[gloves_id], lazy="joined", single_parent=True, cascade="all, delete, delete-orphan")
    leggings_id: Mapped[int] = mapped_column(ForeignKey("items.id"), nullable=True)
    leggings = relationship("Item", foreign_keys=[leggings_id], lazy="joined", single_parent=True, cascade="all, delete, delete-orphan")
    boots_id: Mapped[int] = mapped_column(ForeignKey("items.id"), nullable=True)
    boots = relationship("Item", foreign_keys=[boots_id], lazy="joined", single_parent=True, cascade="all, delete, delete-orphan")

    # Trinkets
    backpack_id: Mapped[int] = mapped_column(ForeignKey("items.id"), nullable=True)
    backpack = relationship("Item", foreign_keys=[backpack_id], lazy="joined", single_parent=True, cascade="all, delete, delete-orphan")
    accessory_1_id: Mapped[int] = mapped_column(ForeignKey("items.id"), nullable=True)
    accessory_1 = relationship("Item", foreign_keys=[accessory_1_id], lazy="joined", single_parent=True, cascade="all, delete, delete-orphan")
    accessory_2_id: Mapped[int] = mapped_column(ForeignKey("items.id"), nullable=True)
    accessory_2 = relationship("Item", foreign_keys=[accessory_2_id], lazy="joined", single_parent=True, cascade="all, delete, delete-orphan")
    amulet_id: Mapped[int] = mapped_column(ForeignKey("items.id"), nullable=True)
    amulet = relationship("Item", foreign_keys=[amulet_id], lazy="joined", single_parent=True, cascade="all, delete, delete-orphan")
    ring_1_id: Mapped[int] = mapped_column(ForeignKey("items.id"), nullable=True)
    ring_1 = relationship("Item", foreign_keys=[ring_1_id], lazy="joined", single_parent=True, cascade="all, delete, delete-orphan")
    ring_2_id: Mapped[int] = mapped_column(ForeignKey("items.id"), nullable=True)
    ring_2 = relationship("Item", foreign_keys=[ring_2_id], lazy="joined", single_parent=True, cascade="all, delete, delete-orphan")

    # Weapons
    weapon_a1_id: Mapped[int] = mapped_column(ForeignKey("items.id"), nullable=True)
    weapon_a1 = relationship("Item", foreign_keys=[weapon_a1_id], lazy="joined", single_parent=True, cascade="all, delete, delete-orphan")
    weapon_a2_id: Mapped[int] = mapped_column(ForeignKey("items.id"), nullable=True)
    weapon_a2 = relationship("Item", foreign_keys=[weapon_a2_id], lazy="joined", single_parent=True, cascade="all, delete, delete-orphan")
    weapon_b1_id: Mapped[int] = mapped_column(ForeignKey("items.id"), nullable=True)
    weapon_b1 = relationship("Item", foreign_keys=[weapon_b1_id], lazy="joined", single_parent=True, cascade="all, delete, delete-orphan")
    weapon_b2_id: Mapped[int] = mapped_column(ForeignKey("items.id"), nullable=True)
    weapon_b2 = relationship("Item", foreign_keys=[weapon_b2_id], lazy="joined", single_parent=True, cascade="all, delete, delete-orphan")

    def __str__(self):
        nl = "\n"
        return f"{nl.join(f'{item.slot.name}: {item}' for item in self.items)}"

    @property
    def items(self) -> List["Item"]:
        lst = []
        for slot in EquipmentSlot:
            if getattr(self, slot.value):
                lst.append(getattr(self, slot.value))
        return lst

    @property
    def weapons(self) -> List["Item"]:
        lst = []
        for slot in EquipmentSlot.get_weapon_slots():
            if getattr(self, slot.value):
                lst.append(getattr(self, slot.value))
        return lst

    def add_item(self, item: "Item"):
        setattr(self, item.slot.value, item)

    def get_item(self, slot: EquipmentSlot):
        return getattr(self, slot.value)

    def get_weapons_str(self) -> str:
        return f"{self.weapon_a1.stats + ' ' + self.weapon_a1.type if self.weapon_a1 else 'None'}/" \
               f"{self.weapon_a2.stats + ' ' + self.weapon_a2.type if self.weapon_a2 else 'None'} and " \
               f"{self.weapon_b1.stats + ' ' + self.weapon_b1.type if self.weapon_b1 else 'None'}/" \
               f"{self.weapon_b2.stats + ' ' + self.weapon_b2.type if self.weapon_b2 else 'None'}"

    def get_weaponset(self, slot: EquipmentSlot):
        match slot:
            case EquipmentSlot.WeaponA1 | EquipmentSlot.WeaponA2:
                return [self.get_item(EquipmentSlot.WeaponA1), self.get_item(EquipmentSlot.WeaponA2)]
            case EquipmentSlot.WeaponB1 | EquipmentSlot.WeaponB2:
                return [self.get_item(EquipmentSlot.WeaponB1), self.get_item(EquipmentSlot.WeaponB2)]
            case _:
                raise Exception(f"{slot} is not a weapon slot")

    def to_embed(self, embed: Embed = Embed(title="Equipment")):
        # Armor
        value = ""
        for slot in EquipmentSlot.get_armor_slots():
            if getattr(self, slot.value):
                value += f"{getattr(self, slot.value)}\n"
        embed.add_field(name="Armor", value=value, inline=False)

        # Trinkets
        value = ""
        for slot in EquipmentSlot.get_trinket_slots():
            if getattr(self, slot.value):
                value += f"{getattr(self, slot.value)}\n"
        embed.add_field(name="Trinkets", value=value, inline=False)

        # Weapons
        value = ""
        for slot in EquipmentSlot.get_weapon_slots():
            if getattr(self, slot.value):
                value += f"{getattr(self, slot.value)}\n"
        embed.add_field(name="Weapons", value=value, inline=False)
        return embed

    def compare(self, other) -> FeedbackCollection:
        fbc = FeedbackCollection()
        fbc.add(self.compare_armor(other))
        fbc.add(self.compare_trinkets(other))
        fbc.add(self.compare_weapons(other))
        return fbc

    def compare_armor(self, other):
        fbg = FeedbackGroup("Armor")
        for slot in EquipmentSlot.get_armor_slots():
            if not other.get_item(slot):
                continue
            if not self.get_item(slot):
                fbg.add(Feedback(f"{other.get_item(slot).type} is missing", FeedbackLevel.ERROR))
                continue
            fbg = self.get_item(slot).check_basics(fbg)
            fbg = self.get_item(slot).compare(other.get_item(slot), fbg)

        if fbg.level <= FeedbackLevel.WARNING:
            fbg.add(Feedback(f"All items are at least exotic", FeedbackLevel.SUCCESS))
        if fbg.level <= FeedbackLevel.SUCCESS:
            fbg.add(Feedback(f"Stats and upgrades of all items are correct", FeedbackLevel.SUCCESS))
        return fbg

    def compare_trinkets(self, other) -> FeedbackGroup:
        self.ring_1 = None
        fbg = FeedbackGroup("Trinkets")
        for slot in [EquipmentSlot.Backpack, EquipmentSlot.Amulet]:
            if not self.get_item(slot):
                fbg.add(Feedback(f"{other.get_item(slot).type} is missing", FeedbackLevel.ERROR))
                continue
            fbg = self.get_item(slot).check_basics(fbg, Rarity.Ascended)
            fbg = self.get_item(slot).compare(other.get_item(slot), fbg)

        for slots in [[EquipmentSlot.Accessory1, EquipmentSlot.Accessory2], [EquipmentSlot.Ring1, EquipmentSlot.Ring2]]:
            # Check if both items exist and get a list of stats
            item_missing = False
            item_stats_self = []
            item_stats_other = []
            for slot in slots:
                if not self.get_item(slot):
                    fbg.add(Feedback(f"{other.get_item(slot).type} is missing", FeedbackLevel.ERROR))
                    item_missing = True
                else:
                    fbg = self.get_item(slot).check_basics(fbg, Rarity.Ascended)
                    item_stats_self.append(self.get_item(slot).stats)
                    item_stats_other.append(other.get_item(slot).stats)
            if item_missing:
                continue

            # Compare stats
            for stat in item_stats_other.copy():
                if stat in item_stats_self:
                    item_stats_self.remove(stat)
                    item_stats_other.remove(stat)

            for stat_self, stat_other in zip(item_stats_self, item_stats_other):
                fbg.add(Feedback(f"Your {stat_self} {self.get_item(slots[0]).type} should be {stat_other}", FeedbackLevel.WARNING))

        if fbg.level <= FeedbackLevel.WARNING:
            fbg.add(Feedback(f"All items are at least ascended", FeedbackLevel.SUCCESS))
        if fbg.level <= FeedbackLevel.SUCCESS:
            fbg.add(Feedback(f"Stats of all items are correct", FeedbackLevel.SUCCESS))
        return fbg

    def compare_weapons(self, other):
        fbgs = []
        self_cp = deepcopy(self)
        for i in range(2):
            for j in range(2):
                fbg = FeedbackGroup("Weapons")
                for slot in EquipmentSlot.get_weapon_slots():
                    if not other.get_item(slot):
                        # Check if the item set has an item where there should be none
                        # In case the other gear has no items in that weapons set we can ignore (and allow) the item
                        # In case the weapon set is not empty then there should not be any additional items, so we break
                        if self_cp.get_item(slot):
                            weapon_set = other.get_weaponset(slot)
                            if weapon_set[0] or weapon_set[1]:
                                break
                        continue
                    if not self_cp.get_item(slot):
                        break
                    if not self_cp.get_item(slot).type == other.get_item(slot).type:
                        break
                    fbg = self_cp.get_item(slot).check_basics(fbg, Rarity.Ascended)
                    fbg = self_cp.get_item(slot).compare(other.get_item(slot), fbg)
                else:
                    # Add positive feedback
                    if fbg.level <= FeedbackLevel.WARNING:
                        fbg.add(Feedback(f"You are using the correct weapons", FeedbackLevel.SUCCESS))
                        fbg.add(Feedback(f"All items are at least ascended", FeedbackLevel.SUCCESS))
                    if fbg.level <= FeedbackLevel.SUCCESS:
                        fbg.add(Feedback(f"Stats and upgrades of all items are correct", FeedbackLevel.SUCCESS))
                    fbgs.append(fbg)

                # Switch offhands
                if j == 0:
                    tmp = deepcopy(self_cp.weapon_a2)
                    self_cp.weapon_a2 = deepcopy(self_cp.weapon_b2)
                    self_cp.weapon_b2 = tmp

            # Switch main hands
            if i == 0:
                self_cp = deepcopy(self)
                self_cp.weapon_a1 = self.weapon_b1
                self_cp.weapon_b1 = self.weapon_a1

        if not fbgs:
            fbg = FeedbackGroup("Weapons")
            fbg.add(Feedback(f"**You are not using the correct weapons:**\n"
                             f"**Your Weapons:** {self.get_weapons_str()}\n"
                             f"**Correct Weapons:** {other.get_weapons_str()}\n",
                             FeedbackLevel.ERROR))
            return fbg

        # Select the feedback with the least errors and return it
        selected = fbgs[0]
        for fbg in fbgs:
            if fbg.level < selected.level:
                selected = fbg
            elif fbg.level == selected.level and len(fbg.feedback) < len(selected.feedback):
                selected = fbg
        return selected
