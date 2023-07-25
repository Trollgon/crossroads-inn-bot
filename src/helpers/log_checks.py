from typing import Dict
from sqlalchemy import select
from database import Session
from models.config import Config
from models.enums.config_key import ConfigKey
from models.enums.log_status import LogStatus
from models.enums.pools import BossLogPool
from models.feedback import FeedbackGroup, FeedbackLevel, Feedback, FeedbackCollection
from models.log import Log


async def check_log(log_json: Dict, account_name: str, tier: int, discord_user_id: int, log_url: str, log: Log) -> FeedbackCollection:
    fbc = FeedbackCollection()

    # Get config
    async with Session.begin() as session:
        config = await Config.to_dict(session)

    # General log checks
    fbg_valid = FeedbackGroup(message="Checking if log is valid")
    fbc.add(fbg_valid)

    for player in log_json["players"]:
        if player['account'] == account_name:
            break
    else:
        fbg_valid.add(Feedback(f"Could not find account {account_name} in log", FeedbackLevel.ERROR))

    # Check version
    if log_json["gW2Build"] < int(config[ConfigKey.MIN_GW2_BUILD]):
        fbg_valid.add(Feedback(f"Log is from before the latest major balance patch.", FeedbackLevel.ERROR))

    async with Session.begin() as session:
        # Checkm if this exact log was already submitted
        stmt = select(Log).where(Log.log_url == log_url).where(Log.discord_user_id == discord_user_id).where(Log.status != LogStatus.DENIED)
        if (await session.execute(stmt)).scalar():
            fbg_valid.add(Feedback(f"You already submitted this log.", FeedbackLevel.ERROR))

        # Check if a log for this boss was already submitted
        stmt = select(Log).where(Log.discord_user_id == discord_user_id) \
            .where(Log.status != LogStatus.DENIED).where(Log.status != LogStatus.REVIEW_DENIED) \
            .where(Log.encounter_id == log_json["eiEncounterID"]).where(Log.tier == tier).where(Log.role == log.role)
        if (await session.execute(stmt)).scalar():
            fbg_valid.add(Feedback(f"You already submitted a log for this boss.", FeedbackLevel.ERROR))

        # Assign boss log pool
        await log.assign_pool(session)

    # Count boss pools
    stmt = select(Log).where(Log.discord_user_id == discord_user_id) \
        .where(Log.status != LogStatus.DENIED).where(Log.status != LogStatus.REVIEW_DENIED).where(Log.tier == tier)
    boss_pools = {pool: 0 for pool in BossLogPool}
    async with Session.begin() as session:
        submitted_logs = (await session.execute(stmt)).scalars().all()

        # Check already submitted logs
        for l in submitted_logs:
            boss_pools[l.assigned_pool] += 1

        # Check this log
        boss_pools[log.assigned_pool] += 1

    # Check boss pool
    if boss_pools[BossLogPool.NOT_ALLOWED]:
        fbg_valid.add(Feedback(f"You submitted a log from a boss that is {BossLogPool.NOT_ALLOWED.value}", FeedbackLevel.ERROR))

    if tier == 2:
        if boss_pools[BossLogPool.POOL_1] > 1:
            fbg_valid.add(Feedback(f"You can only submit one log from pool {BossLogPool.POOL_1.value}", FeedbackLevel.ERROR))
    elif tier == 3:
        if boss_pools[BossLogPool.POOL_1] > 0 or boss_pools[BossLogPool.POOL_2] > 0:
            fbg_valid.add(Feedback(f"You can only submit logs from pool {BossLogPool.POOL_3.value} and {BossLogPool.POOL_4.value}", FeedbackLevel.ERROR))
        if boss_pools[BossLogPool.POOL_3] > 2:
            fbg_valid.add(Feedback(f"At least one log must be from pool {BossLogPool.POOL_4.value}", FeedbackLevel.ERROR))

    # Don't need to check performance if the log is invalid
    if fbg_valid.level == FeedbackLevel.ERROR:
        return fbc

    # General performance checks
    fbg_general = FeedbackGroup(message="Checking performance")
    fbc.add(fbg_general)

    if not log_json["success"]:
        fbg_general.add(Feedback("Boss was not killed", FeedbackLevel.ERROR))

    squad_downs = 0
    squad_deaths = 0
    found_blood_magic = False
    is_emboldened = False
    for player in log_json["players"]:
        if player["account"] == account_name:
            if player["defenses"][0]["deadCount"] > 0:
                fbg_general.add(Feedback(f"You've died. You must be alive at the end of the fight.", FeedbackLevel.ERROR))

            if player["defenses"][0]["downCount"] > int(config[ConfigKey.MAX_PLAYER_DOWNS]):
                fbg_general.add(Feedback(f"You have downed more than {config[ConfigKey.MAX_PLAYER_DOWNS]} times. ({player['defenses'][0]['downCount']})", FeedbackLevel.ERROR))

        squad_downs += player["defenses"][0]["downCount"]
        squad_deaths += player["defenses"][0]["deadCount"]

        for b in player["buffUptimes"]:
            if b["id"] == 29726:
                found_blood_magic = True
            if b["id"] == 68087:
                is_emboldened = True

    if squad_downs > int(config[ConfigKey.MAX_SQUAD_DOWNS]):
        fbg_general.add(Feedback(f"Your squad downed more than {config[ConfigKey.MAX_SQUAD_DOWNS]} times. ({squad_downs})", FeedbackLevel.ERROR))

    if squad_deaths > int(config[ConfigKey.MAX_SQUAD_DEATHS]):
        fbg_general.add(Feedback(f"Your squad died more than {config[ConfigKey.MAX_SQUAD_DEATHS]}. ({squad_deaths})", FeedbackLevel.ERROR))

    if found_blood_magic:
        fbg_general.add(Feedback(f"We do not allow logs with a Blood Magic Necromancer present.", FeedbackLevel.ERROR))

    if is_emboldened:
        fbg_general.add(Feedback(f"We do not allow logs with Emboldened Mode active.", FeedbackLevel.ERROR))

    return fbc