from gw2.models.equipment import *
from gw2.models.feedback import *


def compare_equipment(player_equipment: Equipment, sc_equipment: Equipment) -> FeedbackCollection:
    exotic = Rarity("Exotic")
    fbc = FeedbackCollection(f"Comparing equipment tab {player_equipment.name} to {sc_equipment.name}")

    for slot, sc_item in sc_equipment.items.items():
        player_item: Item = player_equipment.items[slot]

        # Skip aquatic gear
        if "Aquatic" in slot:
            continue
        # Check stats
        if player_item.stats.name != sc_item.stats.name:
            fbc.add(Feedback(f"{player_item.stats} {player_item.name}: Should be {sc_item.stats.name}", FeedbackLevel.WARNING))

        if player_item.rarity < exotic:
            fbc.add(Feedback(f"{player_item.rarity} {player_item.name}: Should be at least {exotic}", FeedbackLevel.ERROR))

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
    return fbc
