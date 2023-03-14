from copy import copy
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
        return f"{self.get_item(EquipmentSlot.WeaponA1).type if self.get_item(EquipmentSlot.WeaponA1) else 'None'}/" \
               f"{self.get_item(EquipmentSlot.WeaponA2).type if self.get_item(EquipmentSlot.WeaponA2) else 'None'} and " \
               f"{self.get_item(EquipmentSlot.WeaponB1).type if self.get_item(EquipmentSlot.WeaponB1) else 'None'}/" \
               f"{self.get_item(EquipmentSlot.WeaponB2).type if self.get_item(EquipmentSlot.WeaponB2) else 'None'}"

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
                fbg.add(Feedback(f"{other.type} is missing", FeedbackLevel.ERROR))
                continue
            fbg = self.get_item(slot).check_basics(fbg)
            fbg = self.get_item(slot).compare(other.get_item(slot), fbg)

        if fbg.level <= FeedbackLevel.WARNING:
            fbg.add(Feedback(f"All items are at least exotic", FeedbackLevel.SUCCESS))
        if fbg.level <= FeedbackLevel.SUCCESS:
            fbg.add(Feedback(f"Stats and upgrades of all items are correct", FeedbackLevel.SUCCESS))
        return fbg

    def compare_trinkets(self, other) -> FeedbackGroup:
        fbg = FeedbackGroup("Trinkets")
        for slot in [EquipmentSlot.Backpack, EquipmentSlot.Amulet]:
            if not self.get_item(slot):
                fbg.add(Feedback(f"{other.type} is missing", FeedbackLevel.ERROR))
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
                    fbg.add(Feedback(f"{other.type} is missing", FeedbackLevel.ERROR))
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
        fbg = FeedbackGroup("Weapons")

        # Create dicts of weapons by weapon type
        weapons_self = {}
        weapons_other = {}
        for slot in EquipmentSlot.get_weapon_slots():
            item_self = self.get_item(slot)
            item_other = other.get_item(slot)
            if item_self:
                weapons_self[item_self.type] = item_self
            if item_other:
                weapons_other[item_other.type] = item_other

        # Check if the player is using the correct weapon types
        weapons_self_lst = list(weapons_self.keys())
        for weapon in weapons_other.keys():
            if weapon in weapons_self.keys():
                weapons_self_lst.remove(weapon)
            else:
                break

        if weapons_self_lst:
            fbg.add(Feedback(f"You are not using the correct weapons. "
                             f"You should be using {other.get_weapons_str()}"
                             f" instead of {self.get_weapons_str()}",
                             FeedbackLevel.ERROR))
            return fbg

        for type in weapons_other.keys():
            weapon_self = weapons_self[type]
            weapon_other = weapons_other[type]

            fbg = weapon_self.check_basics(fbg, Rarity.Ascended)
            fbg = weapon_self.compare(weapon_other, fbg)

        if fbg.level <= FeedbackLevel.WARNING:
            fbg.add(Feedback(f"All items are at least ascended", FeedbackLevel.SUCCESS))
        if fbg.level <= FeedbackLevel.SUCCESS:
            fbg.add(Feedback(f"Stats and upgrades of all items are correct", FeedbackLevel.SUCCESS))
        return fbg
