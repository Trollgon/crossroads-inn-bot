from gw2.api import *

ITEM_SLOT_WHITELIST = ["WeaponA1", "WeaponA2", "WeaponB1", "WeaponB2",
                       "Helm", "Shoulders", "Coat", "Gloves", "Leggings", "Boots",
                       "Backpack", "Accessory1", "Accessory2", "Amulet", "Ring1", "Ring2"]


async def get_equipment(api: API, character: str, tab: int = 1):
    char_data = await api.get_character_data(character)
    equipment_tab_items = None
    for equipment_tab in char_data["equipment_tabs"]:
        if equipment_tab["tab"] == tab:
            equipment_tab_items = equipment_tab

    if not equipment_tab_items:
        raise Exception("Equipment Tab not found")

    equipment = Equipment()
    equipment.name = equipment_tab_items["name"] if equipment_tab_items["name"] else str(equipment_tab_items["tab"])
    items = {}
    for equipment_tab_item in equipment_tab_items["equipment"]:
        # Skip items like underwater weapons and aqua breather
        if not equipment_tab_item["slot"] in ITEM_SLOT_WHITELIST:
            continue

        item = Item()
        item.id = equipment_tab_item["id"]
        item_data = await api.get_item(equipment_tab_item['id'])
        item.name = item_data["name"]
        item.rarity = Rarity(item_data["rarity"])
        item.level = item_data["level"]

        if "type" in item_data["details"]:
            item.type = item_data["details"]["type"]
        else:
            item.type = equipment_tab_item["slot"]

        stats = Stats()
        if "stats" in equipment_tab_item:
            stats.id = equipment_tab_item["stats"]["id"]
            stats.attributes = equipment_tab_item["stats"]["attributes"]
        elif "infix_upgrade" in item_data["details"]:
            stats.id = item_data["details"]["infix_upgrade"]["id"]
            for stat in item_data["details"]["infix_upgrade"]["attributes"]:
                stats.attributes[stat["attribute"]] = stat["modifier"]
        else:
            for equipment_item in char_data["equipment"]:
                if item.id == equipment_item["id"] and equipment_tab_items["tab"] in equipment_item["tabs"] and "stats" in equipment_item:
                    stats.id = equipment_item["stats"]["id"]
                    stats.attributes = equipment_item["stats"]["attributes"]
                    break
            else:
                # TODO: Handle items without stats correctly (e.g. aqua breather on Pamaki)
                print(f"Unable to determine stats for item: {item}")
                continue

        stats_data = await api.get_item_stats(stats.id)
        stats.name = stats_data["name"]
        item.stats = stats

        if "upgrades" in equipment_tab_item:
            upgrades = []
            for upgrade_data in equipment_tab_item["upgrades"]:
                upgrade = Upgrade()
                upgrade.id = upgrade_data
                upgrade.name = (await api.get_item(upgrade.id))["name"]
                upgrades.append(upgrade)
            item.upgrades = upgrades
        items[equipment_tab_item["slot"]] = item
    equipment.items = items
    return equipment


class Equipment:
    name: str = None
    items: dict = {}

    def __str__(self):
        nl = "\n"
        return f"Equipment Name: {self.name}\n{nl.join(f'{slot}: {item}' for slot, item in self.items.items())}"

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

    def get_weapons_str(self) -> str:
        return f"{self.items['WeaponA1'].type if 'WeaponA1' in self.items else 'None'}/"\
               f"{self.items['WeaponA2'].type if 'WeaponA2' in self.items else 'None'} and " \
               f"{self.items['WeaponB1'].type if 'WeaponB1' in self.items else 'None'}/" \
               f"{self.items['WeaponB2'].type if 'WeaponB2' in self.items else 'None'}"



class Rarity:
    def __init__(self, rarity):
        self.name = rarity
        self.__value = ["Junk", "Basic", "Fine", "Masterwork", "Rare", "Exotic", "Ascended", "Legendary"].index(rarity)

    def __str__(self):
        return self.name

    def __lt__(self, other):
        return self.__value < other.__value

    def __le__(self, other):
        return self.__value <= other.__value

    def __eq__(self, other):
        return self.__value == other.__value

    def __ge__(self, other):
        return self.__value >= other.__value

    def __gt__(self, other):
        return self.__value > other.__value


class Stats:
    id: int = None
    name: str = None
    attributes: dict = {}

    def __str__(self):
        return f"{self.name}"


class Upgrade:
    id: int = None
    name: str = None

    def __str__(self):
        return f"{self.name}"


class Item:
    id: int = None
    name: str = "None"
    type: str = "None"
    rarity: Rarity = None
    stats: Stats = None
    level: int = None
    upgrades: list[Upgrade] = []

    def __str__(self):
        string = f"{self.rarity} {self.stats} {self.name}"
        if len(self.upgrades) > 0:
            string += f" ({', '.join(f'{upgrade}' for upgrade in self.upgrades)})"
        return string
