from gw2.models.equipment import *
from gw2.models.feedback import *


def compare_equipment(player_equipment: Equipment, sc_equipment: Equipment) -> (FeedbackCollection, FeedbackCollection, FeedbackCollection):
    exotic = Rarity("Exotic")
    fbc_armor = FeedbackCollection("Armor")
    fbc_weapons = FeedbackCollection("Weapons")
    fbc_trinkets = FeedbackCollection("Trinkets")


    active_fbc = fbc_armor
    for slot, sc_item in sc_equipment.items.items():
        if "Accessory" in slot:
            active_fbc = fbc_trinkets
        if "Weapon" in slot:
            active_fbc = fbc_weapons

        if slot not in player_equipment.items:
            active_fbc.add(Feedback(f"{sc_item.name} is missing", FeedbackLevel.ERROR))
            continue
        player_item: Item = player_equipment.items[slot]

        # Skip aquatic gear
        if "Aquatic" in slot:
            continue
        # Check stats
        if player_item.stats.name != sc_item.stats.name:
            active_fbc.add(Feedback(f"{player_item.stats} {player_item.name}: Should be {sc_item.stats.name}", FeedbackLevel.WARNING))

        if player_item.rarity < exotic:
            active_fbc.add(Feedback(f"{player_item.rarity} {player_item.name}: Should be at least {exotic}", FeedbackLevel.ERROR))

        sc_upgrades = sc_item.upgrades.copy()
        player_upgrades = player_item.upgrades.copy()
        for player_upgrade in player_upgrades:
            for sc_upgrade in sc_upgrades:
                if int(sc_upgrade.id) == int(player_upgrade.id):
                    sc_upgrades.remove(sc_upgrade)
                    player_upgrades.remove(player_upgrade)
        if len(sc_upgrades) != 0 or len(player_upgrades) != 0:
            active_fbc.add(Feedback(f"{player_item.name}: Wrong upgrade ({', '.join(f'{upgrade}' for upgrade in player_upgrades)}"
                             f" instead of {', '.join(f'{upgrade}' for upgrade in sc_upgrades)})", FeedbackLevel.WARNING))

    # Add positive feedback
    for active_fbc in [fbc_armor, fbc_trinkets, fbc_weapons]:
        if active_fbc.level <= FeedbackLevel.WARNING:
            active_fbc.add(Feedback(f"All items are at least exotic", FeedbackLevel.INFO))
        if active_fbc.level <= FeedbackLevel.INFO:
            active_fbc.add(Feedback(f"Stats of all items are correct", FeedbackLevel.INFO))
    return fbc_armor, fbc_weapons, fbc_trinkets
