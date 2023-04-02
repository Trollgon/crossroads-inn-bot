from enum import Enum


class Attribute(Enum):
    Power = "power"
    Precision = "precision"
    Toughness = "toughness"
    Vitality = "vitality"

    BoonDuration = "concentration"
    ConditionDamage = "condition_damage"
    ConditionDuration = "expertise"
    CritDamage = "ferocity"
    Healing = "healing_power"
