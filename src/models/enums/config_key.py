from enum import Enum


class ConfigKey(Enum):
    T1_ROLE_ID = "Tier 1 role id"
    T2_ROLE_ID = "Tier 2 role id"
    T3_ROLE_ID = "Tier 3 role id"
    POWER_DPS_ROLE_ID = "pDPS role id"
    CONDITION_DPS_ROLE_ID = "cDPS role id"
    HEAL_ROLE_ID = "Heal role id"
    BOON_DPS_ROLE_ID = "Boon DPS role id"

    MIN_GW2_BUILD = "Minimum GW2 build version"

    MAX_SQUAD_DOWNS = "Maximum squad downs"
    MAX_SQUAD_DEATHS = "Maximum squad deaths"