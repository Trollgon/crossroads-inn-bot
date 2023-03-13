from enum import Enum


class Rarity(Enum):
    Junk = 0
    Basic = 1
    Fine = 2
    Masterwork = 3
    Rare = 4
    Exotic = 5
    Ascended = 6
    Legendary = 7

    def __str__(self):
        return self.name

    def __lt__(self, other):
        return self.value < other.value

    def __le__(self, other):
        return self.value <= other.value

    def __eq__(self, other):
        return self.value == other.value

    def __ge__(self, other):
        return self.value >= other.value

    def __gt__(self, other):
        return self.value > other.value

    def __hash__(self):
        return hash(self.value)
