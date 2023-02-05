import json
import aiohttp


class API:
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def get_endpoint_v2(self, endpoint: str):
        url = f"https://api.guildwars2.com/v2/{endpoint}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, headers=headers) as resp:
                return await resp.json()

    async def check_key(self) -> bool:
        # Check if api key is valid
        tokeninfo = await self.get_endpoint_v2("tokeninfo")
        if "Invalid access token" in str(tokeninfo):
            return False

        # Check if correct permissions are set
        perms = tokeninfo["permissions"]
        if "account" not in perms:  # Should always be set but check anyway
            return False
        if "progression" not in perms:
            return False
        if "characters" not in perms:
            return False
        return True

    async def get_account_name(self) -> str:
        account = await self.get_endpoint_v2("account")
        return account["name"]

    async def get_characters(self) -> list[str]:
        return await self.get_endpoint_v2("characters")

    async def check_mastery(self) -> bool:
        # get mastery of player
        mastery_list = await self.get_endpoint_v2("account/masteries")

        gliding = False
        jackal = False

        for mastery in mastery_list:
            # check "Ley Line Gliding"
            if mastery["id"] == 8 and mastery["level"] >= 5:
                gliding = True
            # check "Shifting Sands"
            if mastery["id"] == 18 and mastery["level"] >= 2:
                jackal = True

        # check if both are unlocked
        if gliding and jackal:
            return True
        return False

    async def check_kp(self):
        # list of killed bosses
        kp = []

        # load json with achievement ids
        with open("gw2/achievements.json", "r") as json_file:
            bosses = json.load(json_file)

            # get max amount of bosses (-2 to handle statues)
            max_bosses = len(bosses) - 2

        # get achievements of player
        achievements = await self.get_endpoint_v2("account/achievements")

        # check achievements
        for achievement in achievements:
            for boss in bosses:
                # check if achievement is relevant and if it is done
                if boss["achievement"]["id"] == achievement["id"] and achievement["done"]:
                    kp.append(boss["boss"])

        # Combine the 3 statues bosses into a single entry if all 3 were killed
        statues = 0
        if "Statue of Death" in kp:
            kp.remove("Statue of Death")
            statues += 1
        if "Statue of Ice" in kp:
            kp.remove("Statue of Ice")
            statues += 1
        if "Statue of Darkness" in kp:
            kp.remove("Statue of Darkness")
            statues += 1
        if statues == 3:
            kp.append("Statues")

        # check if at least 5 different bosses were killed
        if len(bosses) >= 5:
            return True

    async def get_character_data(self, character_name):
        return await self.get_endpoint_v2(f"characters?v=2021-07-24T00%3A00%3A00Z&id={character_name}")
