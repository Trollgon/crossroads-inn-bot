import copy

from gw2.models.equipment import *
from gw2.models.feedback import *


def compare_weapons(player_equipment: Equipment, reference_equipment: Equipment) -> FeedbackGroup:
    fbg_1 = FeedbackGroup("Weapons")
    fbg_2 = FeedbackGroup("Weapons")

    # Create a copy of the player equipment with swapped weapons
    player_equipment_tmp = copy.deepcopy(player_equipment)
    tmp_1 = player_equipment_tmp.items["WeaponA1"] if "WeaponA1" in player_equipment_tmp.items else None
    tmp_2 = player_equipment_tmp.items["WeaponA2"] if "WeaponA2" in player_equipment_tmp.items else None
    player_equipment_tmp.items["WeaponA1"] = player_equipment_tmp.items["WeaponB1"] if "WeaponB1" in player_equipment_tmp.items else None
    player_equipment_tmp.items["WeaponA2"] = player_equipment_tmp.items["WeaponB2"] if "WeaponB2" in player_equipment_tmp.items else None
    player_equipment_tmp.items["WeaponB1"] = tmp_1
    player_equipment_tmp.items["WeaponB2"] = tmp_2

    # compare both player equipments with the reference equipment
    for fbg, player_eq in [(fbg_1, player_equipment), (fbg_2, player_equipment_tmp)]:
        using_correct_weapons = True
        for slot in ["WeaponA1", "WeaponA2", "WeaponB1", "WeaponB2"]:
            if not compare_item(slot, player_eq, reference_equipment, fbg, Rarity("Ascended")):
                continue

            # If items exist we can also check their type and if upgrades match
            reference_item: Item = reference_equipment.items[slot]
            player_item: Item = player_eq.items[slot]

            # Check item type
            if player_item.type != reference_item.type:
                fbg.add(Feedback(f"Your {player_item.type} has to be a {reference_item.type}",
                                 FeedbackLevel.ERROR))
                using_correct_weapons = False
                continue

            # Check if upgrades exist
            if len(player_item.upgrades) < len(reference_item.upgrades):
                # Legendary weapons sometimes show up without a sigil
                if player_item.rarity == Rarity("Legendary"):
                    fbg.add(Feedback(f"Your {player_item.type} is missing a sigil. "
                                     f"It should have a {' and a '.join(f'{upgrade}' for upgrade in reference_item.upgrades)}",
                                     FeedbackLevel.WARNING))
                    continue
                else:
                    fbg.add(Feedback(f"Your {player_item.type} is missing a sigil. "
                                     f"It needs a {' and a '.join(f'{upgrade}' for upgrade in reference_item.upgrades)}",
                                     FeedbackLevel.ERROR))
                    continue

            # Compare upgrades. Order of upgrades doesn't matter
            sc_upgrades = [upgrade.name for upgrade in reference_item.upgrades]
            player_upgrades = [upgrade.name for upgrade in player_item.upgrades]
            for sc_upgrade in reference_item.upgrades:
                if sc_upgrade.name in player_upgrades:
                    player_upgrades.remove(sc_upgrade.name)
                    sc_upgrades.remove(sc_upgrade.name)

            if len(sc_upgrades) != 0 or len(player_upgrades) != 0:
                fbg.add(Feedback(f"Your {player_item.type} has a {' and '.join(f'{upgrade}' for upgrade in player_upgrades)}"
                                 f" instead of a {' and '.join(f'{upgrade}' for upgrade in sc_upgrades)}",
                                 FeedbackLevel.WARNING))

        # Add positive feedback
        if using_correct_weapons:
            fbg.add(Feedback(f"You are using the correct weapons", FeedbackLevel.SUCCESS))
        if fbg.level <= FeedbackLevel.WARNING:
            fbg.add(Feedback(f"All items are at least ascended", FeedbackLevel.SUCCESS))
        if fbg.level <= FeedbackLevel.SUCCESS:
            fbg.add(Feedback(f"Stats and upgrades of all items are correct", FeedbackLevel.SUCCESS))

    # Select the feedback with the least errors and return it
    if fbg_1.level < fbg_2.level:
        fbg = fbg_1
    elif fbg_1.level > fbg_2.level:
        fbg = fbg_2
    else:
        if len(fbg_1.feedback) <= len(fbg_2.feedback):
            fbg = fbg_1
        else:
            fbg = fbg_2
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
            fbg.add(Feedback(f"Your {player_item.type} has a {player_item.upgrades[0].name} but should have a "
                             f"{reference_item.upgrades[0].name}", FeedbackLevel.WARNING))

    if fbg.level <= FeedbackLevel.WARNING:
        fbg.add(Feedback(f"All items are at least exotic", FeedbackLevel.SUCCESS))
    if fbg.level <= FeedbackLevel.SUCCESS:
        fbg.add(Feedback(f"Stats and upgrades of all items are correct", FeedbackLevel.SUCCESS))
    return fbg


def compare_trinkets(player_equipment: Equipment, reference_equipment: Equipment) -> FeedbackGroup:
    fbg = FeedbackGroup("Trinkets")
    for slot in ["Backpack", "Amulet"]:
        compare_item(slot, player_equipment, reference_equipment, fbg, Rarity("Ascended"))

    for slots in [["Accessory1", "Accessory2"], ["Ring1", "Ring2"]]:
        compare_item_group(slots[0], slots[1], player_equipment, reference_equipment, fbg, Rarity("Ascended"))

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
    if slot not in player_equipment.items or player_equipment.items[slot] is None:
        fbg.add(Feedback(f"{reference_item.type} is missing", FeedbackLevel.ERROR))
        return False
    player_item: Item = player_equipment.items[slot]

    # Compare item stats
    if player_item.stats.name != reference_item.stats.name:
        fbg.add(Feedback(f"Your {player_item.stats.name} {player_item.type} should be {reference_item.stats.name}",
                         FeedbackLevel.WARNING))

    # Check rarity
    if player_item.rarity < min_rarity:
        fbg.add(Feedback(f"Your {player_item.type} has to be at least {min_rarity}", FeedbackLevel.ERROR))

    # Check level
    if player_item.level < 80:
        fbg.add(Feedback(f"Your {player_item.type} has to be a level 80 item", FeedbackLevel.ERROR))
    return True


def compare_item_group(slot_1: str, slot_2: str,
                       player_equipment: Equipment, reference_equipment: Equipment,
                       fbg: FeedbackGroup = FeedbackGroup("Item comparison"),
                       min_rarity: Rarity = Rarity("Exotic")) -> FeedbackGroup:
    fbg_acc_1 = copy.deepcopy(fbg)

    # Compare equipment to reference equipment
    for slot in [slot_1, slot_2]:
        compare_item(slot, player_equipment, reference_equipment, fbg_acc_1, min_rarity)

    # Create a copy of the player equipment with the slots switched
    player_equipment_tmp = copy.deepcopy(player_equipment)
    tmp = player_equipment_tmp.items[slot_1]
    player_equipment_tmp.items[slot_1] = player_equipment_tmp.items[slot_2]
    player_equipment_tmp.items[slot_2] = tmp
    fbg_acc_2 = copy.deepcopy(fbg)

    # Compare equipment with switched slots to reference equipment
    for slot in [slot_1, slot_2]:
        compare_item(slot, player_equipment_tmp, reference_equipment, fbg_acc_2, min_rarity)

    # Check which order has the least mistakes and return feedback from that one
    if len(fbg_acc_1.feedback) <= len(fbg_acc_2.feedback):
        fbg = fbg_acc_1
    else:
        fbg = fbg_acc_2
    return fbg
