import json
import aiohttp
from gw2.models.feedback import *


class API:
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def get_endpoint_v2(self, endpoint: str):
        url = f"https://api.guildwars2.com/v2/{endpoint}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, headers=headers) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    raise Exception(f"{resp.status}: {await resp.text()}")

    async def check_key(self) -> FeedbackGroup:
        fbg = FeedbackGroup("API Key")
        # Check if api key is valid
        tokeninfo = await self.get_endpoint_v2("tokeninfo")
        if "Invalid access token" in str(tokeninfo):
            fbg.add(Feedback("Invalid API Key", FeedbackLevel.ERROR))
            return fbg

        fbg.add(Feedback("API Key is valid", FeedbackLevel.SUCCESS))

        # Check if correct permissions are set
        perms = tokeninfo["permissions"]
        if "account" not in perms:  # Should always be set but check anyway
            fbg.add(Feedback("API Key is missing 'account' permission", FeedbackLevel.ERROR))
        if "progression" not in perms:
            fbg.add(Feedback("API Key is missing 'progression' permission", FeedbackLevel.ERROR))
        if "characters" not in perms:
            fbg.add(Feedback("API Key is missing 'characters' permission", FeedbackLevel.ERROR))

        if fbg.level == FeedbackLevel.SUCCESS:
            fbg.add(Feedback("API Key permissions are set up correctly", FeedbackLevel.SUCCESS))
        return fbg

    async def get_account_name(self) -> str:
        account = await self.get_endpoint_v2("account")
        return account["name"]

    async def get_characters(self) -> list[str]:
        return await self.get_endpoint_v2("characters")

    async def check_mastery(self) -> FeedbackGroup:
        fbg = FeedbackGroup("Masteries")
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

        # add feedback
        if gliding:
            fbg.add(Feedback("Ley Line Gliding is unlocked", FeedbackLevel.SUCCESS))
        else:
            fbg.add(Feedback("Ley Line Gliding is not unlocked", FeedbackLevel.ERROR))
        if jackal:
            fbg.add(Feedback("Shifting Sands is unlocked", FeedbackLevel.SUCCESS))
        else:
            fbg.add(Feedback("Shifting Sands is not unlocked", FeedbackLevel.ERROR))
        return fbg

    async def check_kp(self) -> FeedbackGroup:
        fbg = FeedbackGroup("Killproof")
        bosses_killed = []

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
                    bosses_killed.append(boss["boss"])

        # Combine the 3 statues bosses into a single entry if all 3 were killed
        statues = 0
        if "Statue of Death" in bosses_killed:
            bosses_killed.remove("Statue of Death")
            statues += 1
        if "Statue of Ice" in bosses_killed:
            bosses_killed.remove("Statue of Ice")
            statues += 1
        if "Statue of Darkness" in bosses_killed:
            bosses_killed.remove("Statue of Darkness")
            statues += 1
        if statues == 3:
            bosses_killed.append("Statues")

        # check if at least 5 different bosses were killed
        if len(bosses_killed) >= 5:
            fbg.add(Feedback(f"You have killed {len(bosses_killed)}/{max_bosses} different bosses (5 required)",
                             FeedbackLevel.SUCCESS))
        else:
            fbg.add(Feedback(f"You have killed {len(bosses_killed)}/{max_bosses} different bosses (5 required)",
                             FeedbackLevel.SUCCESS))
        return fbg

    async def get_character_data(self, character_name):
        return await self.get_endpoint_v2(f"characters?v=2021-07-24T00%3A00%3A00Z&id={character_name}")
