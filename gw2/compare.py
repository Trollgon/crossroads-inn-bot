from gw2.models.equipment import *
from gw2.models.feedback import *


def compare_equipment(player_equipment: Equipment, sc_equipment: Equipment) -> FeedbackCollection:
    exotic = Rarity("Exotic")
    fbc = FeedbackCollection(f"Comparing equipment tab {player_equipment.name} to {sc_equipment.name}")
    all_exotic = True
    all_stats_match = True

    for slot, sc_item in sc_equipment.items.items():
        if slot not in player_equipment.items:
            fbc.add(Feedback(f"{sc_item.name} is missing", FeedbackLevel.ERROR))
            continue
        player_item: Item = player_equipment.items[slot]

        # Skip aquatic gear
        if "Aquatic" in slot:
            continue
        # Check stats
        if player_item.stats.name != sc_item.stats.name:
            fbc.add(Feedback(f"{player_item.stats} {player_item.name}: Should be {sc_item.stats.name}", FeedbackLevel.WARNING))
            all_stats_match = False

        if player_item.rarity < exotic:
            fbc.add(Feedback(f"{player_item.rarity} {player_item.name}: Should be at least {exotic}", FeedbackLevel.ERROR))
            all_exotic = False

        sc_upgrades = sc_item.upgrades.copy()
        player_upgrades = player_item.upgrades.copy()
        for player_upgrade in player_upgrades:
            for sc_upgrade in sc_upgrades:
                if int(sc_upgrade.id) == int(player_upgrade.id):
                    sc_upgrades.remove(sc_upgrade)
                    player_upgrades.remove(player_upgrade)
        if len(sc_upgrades) != 0 or len(player_upgrades) != 0:
            fbc.add(Feedback(f"{player_item.name}: Wrong upgrade ({', '.join(f'{upgrade}' for upgrade in player_upgrades)}"
                             f" instead of {', '.join(f'{upgrade}' for upgrade in sc_upgrades)})", FeedbackLevel.WARNING))

    # Add positive feedback
    if all_exotic:
        fbc.add(Feedback(f"All items are at least exotic", FeedbackLevel.INFO))
    if all_stats_match:
        fbc.add(Feedback(f"Stats of all items are correct", FeedbackLevel.INFO))
    return fbc
