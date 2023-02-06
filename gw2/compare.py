from gw2.models.equipment import *
from gw2.models.feedback import *


def compare_equipment(player_equipment: Equipment, sc_equipment: Equipment) -> (FeedbackGroup, FeedbackGroup, FeedbackGroup):
    exotic = Rarity("Exotic")
    fbg_armor = FeedbackGroup("Armor")
    fbg_weapons = FeedbackGroup("Weapons")
    fbg_trinkets = FeedbackGroup("Trinkets")


    active_fbg = fbg_armor
    for slot, sc_item in sc_equipment.items.items():
        if "Accessory" in slot:
            active_fbg = fbg_trinkets
        if "Weapon" in slot:
            active_fbg = fbg_weapons

        if slot not in player_equipment.items:
            active_fbg.add(Feedback(f"{sc_item.name} is missing", FeedbackLevel.ERROR))
            continue
        player_item: Item = player_equipment.items[slot]

        # Skip aquatic gear
        if "Aquatic" in slot:
            continue
        # Check stats
        if player_item.stats.name != sc_item.stats.name:
            active_fbg.add(Feedback(f"{player_item.stats} {player_item.name}: Should be {sc_item.stats.name}", FeedbackLevel.WARNING))

        if player_item.rarity < exotic:
            active_fbg.add(Feedback(f"{player_item.rarity} {player_item.name}: Should be at least {exotic}", FeedbackLevel.ERROR))

        sc_upgrades = sc_item.upgrades.copy()
        player_upgrades = player_item.upgrades.copy()
        for player_upgrade in player_upgrades:
            for sc_upgrade in sc_upgrades:
                if int(sc_upgrade.id) == int(player_upgrade.id):
                    sc_upgrades.remove(sc_upgrade)
                    player_upgrades.remove(player_upgrade)
        if len(sc_upgrades) != 0 or len(player_upgrades) != 0:
            active_fbg.add(Feedback(f"{player_item.name}: Wrong upgrade ({', '.join(f'{upgrade}' for upgrade in player_upgrades)}"
                             f" instead of {', '.join(f'{upgrade}' for upgrade in sc_upgrades)})", FeedbackLevel.WARNING))

    # Add positive feedback
    for active_fbg in [fbg_armor, fbg_trinkets, fbg_weapons]:
        if active_fbg.level <= FeedbackLevel.WARNING:
            active_fbg.add(Feedback(f"All items are at least exotic", FeedbackLevel.SUCCESS))
        if active_fbg.level <= FeedbackLevel.SUCCESS:
            active_fbg.add(Feedback(f"Stats of all items are correct", FeedbackLevel.SUCCESS))
    return fbg_armor, fbg_weapons, fbg_trinkets
