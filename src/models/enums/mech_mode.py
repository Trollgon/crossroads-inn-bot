from enum import Enum

class MechMode(Enum):
    PLAYER = "player"
    SQUAD = "squad"

    def __str__(self):
        return self.value