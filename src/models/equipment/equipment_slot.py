from enum import Enum


class EquipmentSlot(Enum):
    # Armor
    Helm = "helm"
    Shoulders = "shoulders"
    Coat = "coat"
    Gloves = "gloves"
    Leggings = "leggings"
    Boots = "boots"

    # Trinkets
    Backpack = "backpack"
    Accessory1 = "accessory_1"
    Accessory2 = "accessory_2"
    Amulet = "amulet"
    Ring1 = "ring_1"
    Ring2 = "ring_2"

    # Weapons
    WeaponA1 = "weapon_a1"
    WeaponA2 = "weapon_a2"
    WeaponB1 = "weapon_b1"
    WeaponB2 = "weapon_b2"
