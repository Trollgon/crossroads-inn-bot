from bs4 import BeautifulSoup
from gw2.models.equipment import *
import os
import aiohttp


async def sc_get(url):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://snowcrows.com" + url) as r:
            return await r.read()


async def get_sc_equipment(api: API, url: str):
    resp = await sc_get(url)
    sc_soup = BeautifulSoup(resp.decode("utf-8"), "html.parser")
    table_data = sc_soup.find_all("td")

    equipment = Equipment()
    equipment.name = f"[{sc_soup.find_all('h1', {'class': 'font-sans font-bold text-5xl m-0 p-0'})[0].text}]" \
                     f"(https://snowcrows.com{url})"
    mh, oh, ring, accessory = 1, 1, 1, 1
    items = {}
    for i in range(0, len(table_data), 2):
        div = table_data[i].div
        item = Item()
        item.id = div["data-armory-ids"]
        item_data = await api.get_item(item.id)
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
        stats_data = await api.get_item_stats(stats.id)
        stats.name = stats_data["name"]
        item.stats = stats

        upgrade_ids = []
        if f"data-armory-{item.id}-upgrades" in str(div):
            upgrade_ids = div[f"data-armory-{item.id}-upgrades"].split(",")
        upgrades = []
        for upgrade_id in upgrade_ids:
            upgrade = Upgrade()
            upgrade.id = int(upgrade_id)
            upgrade.name = (await api.get_item(upgrade.id))["name"]
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


professions = [
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


async def init_builds():
    if os.path.isfile("gw2/builds.json"):
        return
    builds = {}
    for profession in professions:
        # Get recommended builds for this profession
        builds[profession] = await get_sc_builds(profession)

    store_builds(builds)
    print("builds initialized")


def get_builds(profession: professions = None):
    if not os.path.isfile("gw2/builds.json"):
        raise Exception("No builds found")

    with open("gw2/builds.json", "r") as f:
        builds = json.loads(f.read())

    if profession:
        return {profession: builds[profession]}
    return builds


def store_builds(builds: dict):
    with open("gw2/builds.json", "w") as f:
        f.write(json.dumps(builds))


async def add_build(url: str):
    builds = get_builds()
    resp = await sc_get(url)
    sc_soup = BeautifulSoup(resp.decode("utf-8"), "html.parser")
    title = sc_soup.find_all("h1", {"class": "font-sans font-bold text-5xl m-0 p-0"})[0].text
    profession = sc_soup.find_all("a", {"class": "-top-1 relative inline-block lg:inline bg-black bg-opacity-30 py-1.5 px-4 rounded"})[0].text.split(" ")[0]
    profession_builds = builds[profession]
    profession_builds[title] = url
    store_builds(builds)


def remove_build(url: str):
    builds = get_builds()
    for profession in builds:
        for build in builds[profession]:
            if builds[profession][build] == url:
                del builds[profession][build]
                store_builds(builds)
                return
    else:
        print("build not found")

