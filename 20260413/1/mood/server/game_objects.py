"""Game objects."""


class Field:
    """Game field."""

    def __init__(self, size_x=10, size_y=10, start_x=0, start_y=0):
        """Initialize game field."""
        self.players = {}
        self.monsters = {}
        self.monster_types = []
        self.custom_monsters = {}
        self.size_x = size_x
        self.size_y = size_y
        self.weapons = {"sword": 10, "spear": 15, "axe": 20}
        self.fl_movemonsters = True


class Player:
    """Player."""

    def __init__(self, name, writer, size_x=10, size_y=10,
                 start_x=0, start_y=0):
        """Initialize player."""
        self.name = name
        self.writer = writer
        self.x = start_x % size_x
        self.y = start_y % size_y