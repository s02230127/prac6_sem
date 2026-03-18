import sys
from io import StringIO
import shlex
import cowsay
import cmd

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
        self.weapons = {}
        self.size_x = size_x
        self.size_y = size_y


def field_addmon(field, line):
    stats = {}
    try:
        line = shlex.split(line)
    except ValueError:
        raise ValueError(INVALID_ARGS)

    if len(line) != 8:
        raise ValueError(INVALID_ARGS)

    if line[0] not in cowsay.list_cows() and line[0] not in field.monster_types:
        raise ValueError(UNKNOWN_MONSTER)
    stats['name'] = line[0]
    
    try:
        ind = line.index('hello')
        stats['hello'] = line[ind + 1]
        del line[ind:ind + 2]
    except (IndexError, ValueError):
        raise ValueError(INVALID_ARGS)

    try:
        ind = line.index('hp')
        hp = line[ind + 1]
        if hp.isdigit() and int(hp) > 0:
            stats['hp'] = int(hp)
        else:
            raise ValueError(INVALID_ARGS)
    except (IndexError, ValueError):
        raise ValueError(INVALID_ARGS)

    try:
        ind = line.index('coords')
        x = int(line[ind + 1])
        y = int(line[ind + 2])
        if not(0 <= x < field.size_x and 0 <= y < field.size_y):
            raise ValueError(INVALID_ARGS)
    except (IndexError, ValueError):
        raise ValueError(INVALID_ARGS)

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


def player_attack(field, line):
    args = shlex.split(line)
    weapon = 'sword'
    if len(args) != 0:
        if len(args) != 2:
            print("Invalid arguments")
            return

        if args[0] != 'with':
            print("Invalid arguments")
            return
        
        if args[1] not in field.weapons:
            print("Unknown weapon")
            return

        weapon = args[1]
    
    if field.player not in field.monsters:
        print("No monster here")
        return


        
        
    damage = field.weapons[weapon]
    monster = field.monsters[field.player]
    hp_before = monster['hp']
    hp_after = hp_before - damage if hp_before - damage >= 0 else 0

    print(f"Attacked {monster['name']},  damage {hp_before - hp_after} hp")
    if hp_after == 0:
        del field.monsters[field.player]
        print(f"{monster['name']} died")
    else:
        monster['hp'] = hp_after
        print(f"{monster['name']} now has {monster['hp']}")


def add_monster_type(field):
    jgsbat = cowsay.read_dot_cow(StringIO(r"""
$the_cow = <<EOC;
        $thoughts
            $thoughts
    ,_                    _,
    ) '-._  ,_    _,  _.-' (
    )  _.-'.|\\\--//|.'-._  (
     )'   .'\/o\/o\/'.   `(
      ) .' . \====/ . '. (
       )  / <<    >> \  (
        '-._/``  ``\_.-'
  jgs     __\\\'--'//__
         (((""`  `"")))
EOC
    """))
    
    field.monster_types['jgsbat'] = jgsbat


def set_weapon(field):
    weapons = {"sword": 10, "spear": 15, "axe": 20}
    field.weapons = weapons

class MyGame(cmd.Cmd):
    intro = "<<< Welcome to Python-MUD 0.1 >>>"
    prompt = ""

    def __init__(self):
        self.field = Field(SIZE_X, SIZE_Y, START_X, START_Y)
        add_monster_type(self.field)
        set_weapon(self.field)
        super().__init__()

    def do_down(self, arg):
        player_moving(self.field, "down")

    def do_up(self, arg):
        player_moving(self.field, "up")

    def do_left(self, arg):
        player_moving(self.field, "left")

    def do_right(self, arg):
        player_moving(self.field, "right")

    def do_addmon(self, arg):
        try:
            field_addmon(self.field, arg)
        except ValueError as error:
            if error.args[0] == INVALID_ARGS:
                print("Invalid arguments")
            elif error.args[0] == UNKNOWN_MONSTER:
                print("Cannot add unknown monster")

    def do_attack(self, arg):
        player_attack(self.field, arg)

    def complete_attack(self, text, line, begidx, endidx):
        arg = shlex.split(line)
        if len(arg) == 1:
            return ["with"]

        if len(arg) == 2 and arg[-1] == 'with':
            return list(self.field.weapons)

        if len(arg) != 3:
            return []
        return [wpn for wpn in self.field.weapons if wpn.startswith(text)]




    def emptyline(self):
        pass

    def default(self, line):
        if not line.strip():
            return
        print("Unknown command")
    
    def do_exit(self, arg):
        print("Goodbye")
        return True
    
    def do_EOF(self, arg):
        print("Goodbye")
        return True

if __name__ == '__main__':
    MyGame().cmdloop()
