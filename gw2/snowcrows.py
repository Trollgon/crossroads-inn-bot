import aiohttp
from bs4 import BeautifulSoup
from gw2.api import *
from gw2.models.equipment import *
import typing


async def sc_get(url):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://snowcrows.com" + url) as r:
            return await r.read()


async def get_sc_equipment(api: API, url: str):
    resp = await sc_get(url)
    sc_soup = BeautifulSoup(resp.decode("utf-8"), "html.parser")
    table_data = sc_soup.find_all("td")

    equipment = Equipment()
    equipment.name = url.split("/")[-1]
    mh, oh, ring, accessory = 1, 1, 1, 1
    items = {}
    for i in range(0, len(table_data), 2):
        div = table_data[i].div
        item = Item()
        item.id = div["data-armory-ids"]
        item_data = await api.get_endpoint_v2(f"items/{item.id}")
        item.name = item_data["name"]
        item.rarity = Rarity(item_data["rarity"])

        if item_data["type"] == "UpgradeComponent":
            break

        stats = Stats()
        if f"data-armory-{item.id}-stat" in str(div):
            stats.id = div[f"data-armory-{item.id}-stat"]
        elif "infix_upgrade" in item_data["details"]:
            stats.id = item_data["details"]["infix_upgrade"]["id"]
            for stat in item_data["details"]["infix_upgrade"]["attributes"]:
                stats.attributes[stat["attribute"]] = stat["modifier"]
        stats_data = await api.get_endpoint_v2(f"itemstats/{stats.id}")
        stats.name = stats_data["name"]
        item.stats = stats

        upgrade_ids = []
        if f"data-armory-{item.id}-upgrades" in str(div):
            upgrade_ids = div[f"data-armory-{item.id}-upgrades"].split(",")
        upgrades = []
        for upgrade_id in upgrade_ids:
            upgrade = Upgrade()
            upgrade.id = int(upgrade_id)
            upgrade.name = (await api.get_endpoint_v2(f"items/{upgrade.id}"))["name"]
            upgrades.append(upgrade)
        item.upgrades = upgrades

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

        items[slot] = item
    equipment.items = items
    return equipment


professions = typing.Literal[
    "Guardian", "Warrior", "Revenant",
    "Engineer", "Ranger", "Thief",
    "Elementalist", "Mesmer", "Necromancer"
]


async def get_sc_builds(profession: professions):
    resp = await sc_get(f"/en/builds?profession={profession}&category=recommended")
    sc_soup = BeautifulSoup(resp.decode("utf-8"), "html.parser")

    links = []
    for link in sc_soup.find_all("a", href=True):
        if link["href"].startswith("/en/builds/"):
            links.append(link["href"])

    builds = {}
    for i, build_name in enumerate(sc_soup.find_all("h2", {"class": "block font-medium w-60"})):
        builds[build_name.text] = links[i]
    return builds
