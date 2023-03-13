from typing import List

from sqlalchemy import ForeignKey

from models.base import Base
from discord import Embed
from sqlalchemy.orm import Mapped, mapped_column, relationship

ITEM_SLOT_WHITELIST = ["WeaponA1", "WeaponA2", "WeaponB1", "WeaponB2",
                       "Helm", "Shoulders", "Coat", "Gloves", "Leggings", "Boots",
                       "Backpack", "Accessory1", "Accessory2", "Amulet", "Ring1", "Ring2"]


class Equipment(Base):
    __tablename__ = "equipment"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    # application_id: Mapped[int] = mapped_column(ForeignKey("application.id"))
    # application = relationship("Application", back_populates="equipment")

    # item_ids: Mapped[List[int]] = mapped_column(ForeignKey("items.id"), nullable=True)
    # items: Mapped[List["Item"]] = relationship(foreign_keys=[item_ids], single_parent=True, cascade="all, delete, delete-orphan", lazy="joined", uselist=True)

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
        return f"Equipment Name: {self.name}\n"

    @property
    def items(self) -> List["Item"]:
        lst = []
        for item in [self.helm, self.shoulders, self.coat, self.gloves, self.leggings, self.boots,
                     self.backpack, self.accessory1, self.accessory2, self.amulet, self.ring1, self.ring2,
                     self.weapon_a1, self.weapon_a2, self.weapon_b1, self.weapon_b2]:
            if item:
                lst.append(item)
        return lst

    def to_embed(self, embed: Embed = Embed(title="Equipment")):
        # Armor
        value = ""
        for slot in ITEM_SLOT_WHITELIST[4:10]:
            if slot in self.items:
                value += f"{self.items[slot].stats} {self.items[slot].type} ({self.items[slot].upgrades[0]})\n"
        embed.add_field(name="Armor", value=value, inline=False)

        # Trinkets
        value = ""
        for slot in ITEM_SLOT_WHITELIST[10:]:
            if slot in self.items:
                value += f"{self.items[slot].stats} {self.items[slot].type}\n"
        embed.add_field(name="Trinkets", value=value, inline=False)

        # Weapons
        value = ""
        for slot in ITEM_SLOT_WHITELIST[:4]:
            if slot in self.items:
                value += f"{self.items[slot].stats} {self.items[slot].type} ({', '.join(f'{upgrade}' for upgrade in self.items[slot].upgrades)})\n"
        embed.add_field(name="Weapons", value=value, inline=False)
        return embed
