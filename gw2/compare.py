from gw2.models.equipment import *
from gw2.models.feedback import *


def compare_weapons(player_equipment: Equipment, reference_equipment: Equipment) -> FeedbackGroup:
    fbg = FeedbackGroup("Weapons")

    for slot in ["WeaponA1", "WeaponA2", "WeaponB1", "WeaponB2"]:
        if not compare_item(slot, player_equipment, reference_equipment, fbg, Rarity("Ascended")):
            continue

        # If items exist we can also check if upgrades match
        reference_item: Item = reference_equipment.items[slot]
        player_item: Item = player_equipment.items[slot]
        sc_upgrades = reference_item.upgrades.copy()
        player_upgrades = player_item.upgrades.copy()
        for player_upgrade in player_upgrades:
            for sc_upgrade in sc_upgrades:
                if int(sc_upgrade.id) == int(player_upgrade.id):
                    sc_upgrades.remove(sc_upgrade)
                    player_upgrades.remove(player_upgrade)
        if len(sc_upgrades) != 0 or len(player_upgrades) != 0:
            fbg.add(Feedback(f"Your {player_item.name} has a{' and '.join(f'{upgrade}' for upgrade in player_upgrades)}"
                             f" instead of {' and '.join(f'{upgrade}' for upgrade in sc_upgrades)}", FeedbackLevel.WARNING))

    if fbg.level <= FeedbackLevel.WARNING:
        fbg.add(Feedback(f"All items are at least ascended", FeedbackLevel.SUCCESS))
    if fbg.level <= FeedbackLevel.SUCCESS:
        fbg.add(Feedback(f"Stats and upgrades of all items are correct", FeedbackLevel.SUCCESS))
    return fbg


def compare_armor(player_equipment: Equipment, reference_equipment: Equipment) -> FeedbackGroup:
    fbg = FeedbackGroup("Armor")

    for slot in ["Helm", "Shoulders", "Coat", "Gloves", "Leggings", "Boots"]:
        if not compare_item(slot, player_equipment, reference_equipment, fbg, Rarity("Exotic")):
            continue

        # If items exist we can also check if upgrade matches
        player_item: Item = player_equipment.items[slot]
        reference_item: Item = reference_equipment.items[slot]
        if player_item.upgrades[0].id != reference_item.upgrades[0].id:
            fbg.add(Feedback(f"Your {player_item.name} has a {player_item.upgrades[0].name} but should have a "
                             f"{reference_item.upgrades[0].name}", FeedbackLevel.WARNING))

    if fbg.level <= FeedbackLevel.WARNING:
        fbg.add(Feedback(f"All items are at least exotic", FeedbackLevel.SUCCESS))
    if fbg.level <= FeedbackLevel.SUCCESS:
        fbg.add(Feedback(f"Stats and upgrades of all items are correct", FeedbackLevel.SUCCESS))
    return fbg


def compare_trinkets(player_equipment: Equipment, reference_equipment: Equipment) -> FeedbackGroup:
    fbg = FeedbackGroup("Trinkets")
    for slot in ["Backpack", "Accessory1", "Accessory2", "Amulet", "Ring1", "Ring2"]:
        compare_item(slot, player_equipment, reference_equipment, fbg, Rarity("Ascended"))

    if fbg.level <= FeedbackLevel.WARNING:
        fbg.add(Feedback(f"All items are at least ascended", FeedbackLevel.SUCCESS))
    if fbg.level <= FeedbackLevel.SUCCESS:
        fbg.add(Feedback(f"Stats of all items are correct", FeedbackLevel.SUCCESS))
    return fbg


def compare_item(slot: str,
                 player_equipment: Equipment, reference_equipment: Equipment,
                 fbg: FeedbackGroup = FeedbackGroup("Item comparison"),
                 min_rarity: Rarity = Rarity("Exotic")) -> bool:
    # Check if items exist
    if slot not in reference_equipment.items:
        return False
    reference_item: Item = reference_equipment.items[slot]
    if slot not in player_equipment.items:
        fbg.add(Feedback(f"{reference_item.name} is missing", FeedbackLevel.ERROR))
        return False
    player_item: Item = player_equipment.items[slot]

    # Compare Item stats
    if player_item.stats.name != reference_item.stats.name:
        fbg.add(Feedback(f"Your {player_item.name} is {player_item.stats.name} but should be {reference_item.stats.name}",
                         FeedbackLevel.WARNING))

    # Check rarity
    if player_item.rarity < min_rarity:
        fbg.add(Feedback(f"Your {player_item.name} has to be at least {min_rarity}", FeedbackLevel.ERROR))
    return True
