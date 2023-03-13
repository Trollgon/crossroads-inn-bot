from typing import List
from sqlalchemy import ForeignKey
from discord import Embed
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base
from models.equipment.equipment_slot import EquipmentSlot


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

    def add_item(self, item: "Item"):
        setattr(self, item.slot.value, item)

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