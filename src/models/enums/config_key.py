from enum import Enum


class ConfigKey(Enum):
    T0_ROLE_ID = "Tier 0 role id"
    T1_ROLE_ID = "Tier 1 role id"
    T2_ROLE_ID = "Tier 2 role id"
    T3_ROLE_ID = "Tier 3 role id"
    POWER_DPS_ROLE_ID = "pDPS role id"
    CONDITION_DPS_ROLE_ID = "cDPS role id"
    HEAL_ROLE_ID = "Heal role id"
    BOON_DPS_ROLE_ID = "Boon DPS role id"

    LOG_CHANNEL_ID = "log channel id"
    RR_CHANNEL_ID = "roleright channel id"
    TIER_ASSIGNMENT_CHANNEL_ID = "tier assignment channel id"

    MIN_GW2_BUILD = "Minimum GW2 build version"

    MAX_SQUAD_DOWNS = "Maximum squad downs"
    MAX_SQUAD_DEATHS = "Maximum squad deaths"

    MAX_PLAYER_DOWNS = "Maximum player downs"