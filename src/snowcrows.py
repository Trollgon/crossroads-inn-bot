from bs4 import BeautifulSoup
import aiohttp
from models.build import Build
from models.equipment import Equipment
from models.enums.equipment_slot import EquipmentSlot
from models.item import Item
from models.enums.rarity import Rarity
from api import API


async def sc_get(url):
    if not url.startswith("https://snowcrows.com/"):
        raise ValueError("Only snowcrows links are allowed")

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            return await r.read()


async def get_sc_equipment(url: str, api: API = API("")) -> Build:
    resp = await sc_get(url)
    sc_soup = BeautifulSoup(resp.decode("utf-8"), "html.parser")
    table_data = sc_soup.find_all("td")
    build = Build()
    build.name = f"{sc_soup.find_all('h1', {'class': 'font-sans font-bold text-5xl m-0 p-0'})[0].text}"
    build.url = url
    equipment = Equipment()
    mh, oh, ring, accessory = 1, 1, 1, 1
    for i in range(0, len(table_data), 2):
        div = table_data[i].div
        item = Item()
        item.item_id = div["data-armory-ids"]
        item_data = await api.get_item(item.item_id)
        item.name = item_data["name"]
        item.rarity = Rarity[item_data["rarity"]]
        item.level = item_data["level"]

        if item_data["type"] == "UpgradeComponent":
            break

        if f"data-armory-{item.item_id}-stat" in str(div):
            stats_id = div[f"data-armory-{item.item_id}-stat"]
        elif "infix_upgrade" in item_data["details"]:
            stats_id = item_data["details"]["infix_upgrade"]["id"]
        else:
            print(str(div))
            raise Exception(f"Unable to determine stats for {item.name} on {url}")
        stats_data = await api.get_item_stats(stats_id)
        item.stats = stats_data["name"]

        upgrade_ids = []
        if f"data-armory-{item.item_id}-upgrades" in str(div):
            upgrade_ids = div[f"data-armory-{item.item_id}-upgrades"].split(",")
        for upgrade_id in upgrade_ids:
            item.add_upgrade((await api.get_item(int(upgrade_id)))["name"])

        slot = table_data[i + 1].p.span.string

        if slot == "Main Hand":
            slot = f"Weapon{'A' if mh == 1 else 'B'}1"
            mh += 1
        if slot == "Off Hand":
            slot = f"Weapon{'A' if oh == 1 and mh == 2 else 'B'}2"
            oh += 1
        if slot == "Ring":
            slot = f"Ring{ring}"
            ring += 1
        if slot == "Accessory":
            slot = f"Accessory{accessory}"
            accessory += 1
        if slot == "Backpiece":
            slot = "Backpack"

        if "type" in item_data["details"]:
            item.type = item_data["details"]["type"]
        else:
            item.type = slot
        item.slot = EquipmentSlot[slot]
        equipment.add_item(item)
    build.equipment = equipment
    return build