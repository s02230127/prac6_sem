import sys
import re
import cowsay

SIZE_X = 10
SIZE_Y = 10
START_X = 0
START_Y = 0

UNKNOWN_MONSTER = 1
INVALID_ARGS = 2


class Field:
    def __init__(self, size_x=10, size_y=10, start_x=0, start_y=0):
        self.player = (start_x % size_x, start_y % size_y)
        self.monsters = {}
        self.size_x = size_x
        self.size_y = size_y


def field_addmon(field, line):
    if (matched := re.search(r'^addmon\s+(\S+)\s+(\d+)\s+(\d+)\s+(\S+)$', line)):
        x = int(matched.group(2))
        y = int(matched.group(3))
        if not (0 <= x < field.size_x and 0 <= y < field.size_y):
            raise ValueError(INVALID_ARGS)
        
        word = matched.group(4)
        name = matched.group(1)

        if name not in cowsay.list_cows():
            raise ValueError(UNKNOWN_MONSTER)
        fl_replaced = (x, y) in field.monsters
        field.monsters[(x, y)] = {'name': name, 'word': word}
        print(f"Added monster {name} to ({x}, {y}) saying {word}")
        if fl_replaced:
            print("Replaced the old monster")
    else:
        raise ValueError(INVALID_ARGS)


def encounter(field, x, y):
    print(cowsay.cowsay(field.monsters[(x, y)]['word'], cow=field.monsters[(x, y)]['name']))


def player_moving(field, line):
    if line == 'up':
        field.player = (field.player[0], (field.player[1] - 1) % field.size_y)

    elif line == 'down':
        field.player = (field.player[0], (field.player[1] + 1) % field.size_y)

    elif line == 'right':
        field.player = ((field.player[0] + 1) % field.size_x, field.player[1])

    elif line == 'left':
        field.player = ((field.player[0] - 1) % field.size_x, field.player[1])

    x, y = field.player
    print(f"Moved to ({x}, {y})")

    if (x, y) in field.monsters:
        encounter(field, x, y)


def command_reader(field):
    for line in sys.stdin:
        line = line.strip()

        if not line:
            continue

        if line in ("up", "down", "left", "right"):
            player_moving(field, line)
        elif line.split()[0] == "addmon":
            try:
                field_addmon(field, line)
            except ValueError as error:
                if error.args[0] == INVALID_ARGS:
                    print("Invalid arguments")
                elif error.args[0] == UNKNOWN_MONSTER:
                    print("Cannot add unknown monster")
        else:
            print("Invalid command")


def game():
    field = Field(SIZE_X, SIZE_Y, START_X, START_Y)
    command_reader(field)


if __name__ == '__main__':
    game()