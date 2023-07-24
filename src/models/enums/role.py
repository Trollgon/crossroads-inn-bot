from enum import Enum

from models.enums.config_key import ConfigKey


class Role(Enum):
    NONE = "None"
    POWER_DPS = "pDPS"
    CONDITION_DPS = "cDPS"
    HEAL = "Heal"
    BOON_DPS = "Boon DPS"

    def get_config_key(self) -> ConfigKey:
        match self:
            case Role.POWER_DPS:
                return ConfigKey.POWER_DPS_ROLE_ID
            case Role.CONDITION_DPS:
                return ConfigKey.CONDITION_DPS_ROLE_ID
            case Role.HEAL:
                return ConfigKey.HEAL_ROLE_ID
            case Role.BOON_DPS:
                return ConfigKey.BOON_DPS_ROLE_ID
            case Role.NONE:
                raise ValueError("Cannot get config key for role 'None'")