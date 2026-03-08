import sys
from io import StringIO
import shlex
import cowsay
import re

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
        self.monster_types = {}
        self.size_x = size_x
        self.size_y = size_y


def field_addmon(field, line):
    stats = {}
    line = shlex.split(line)

    if "addmon" != line[0]:
        raise ValueError(INVALID_ARGS)
    if line[1] not in cowsay.list_cows() and line[1] not in field.monster_types:
        raise ValueError(UNKNOWN_MONSTER)
    stats['name'] = line[1]

    if 'hello' not in line:
        raise ValueError(INVALID_ARGS)
    ind = line.index('hello')
    stats['hello'] = line[ind + 1]

    ind = line.index('hp')
    hp = line[ind + 1]
    if hp.isdigit() and int(hp) > 0:
        stats['hp'] = int(hp)
    else:
        raise ValueError(INVALID_ARGS)

    ind = line.index('coords')
    x = int(line[ind + 1])
    y = int(line[ind + 2])
    
    fl_replaced = (x, y) in field.monsters
    field.monsters[(x, y)] = stats
    print(f"Added monster {stats['name']} to ({x}, {y}) saying {stats['hello']}")
    if fl_replaced:
        print("Replaced the old monster")



def encounter(field, x, y):
    if field.monsters[(x, y)]['name'] in field.monster_types:
        monster = field.monster_types[field.monsters[(x, y)]['name']]
        print(cowsay.cowsay(field.monsters[(x, y)]['hello'], cowfile=monster))
    else:
        monster = field.monsters[(x, y)]['name']
        print(cowsay.cowsay(field.monsters[(x, y)]['hello'], cow=monster))



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
 

def add_monster_type(field):
    jgsbat = cowsay.read_dot_cow(StringIO(r"""
        $the_cow = <<EOC;
              $thoughts
                  $thoughts
        ,_                    _,
        ) '-._  ,_    _,  _.-' (
        )  _.-'.|\\--//|.'-._  (
         )'   .'\/o\/o\/'.   `(
          ) .' . \====/ . '. (
           )  / <<    >> \  (
            '-._/``  ``\_.-'
      jgs     __\\'--'//__
             (((""`  `"")))
    EOC
    """))
    
    field.monster_types['jgsbat'] = jgsbat


def game():
    print("<<< Welcome to Python-MUD 0.1 >>>")
    field = Field(SIZE_X, SIZE_Y, START_X, START_Y)
    add_monster_type(field)
    command_reader(field)


if __name__ == '__main__':
    game()
