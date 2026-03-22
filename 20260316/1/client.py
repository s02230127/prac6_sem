import socket
import cmd
import shlex
import cowsay
from io import StringIO
import json

HOST = "localhost"
PORT = 7779

UNKNOWN_MONSTER = 1
INVALID_ARGS = 2


class Field_attributes:
    def __init__(self):
        self.monsters = cowsay.list_cows()
        self.custom_monsters = {}
        self.size_x = 10
        self.size_y = 10
        self.weapons = ["spear", "axe", "sword"]

class MUDClient(cmd.Cmd):
    intro = "<<< Welcome to Python-MUD 0.1 >>>"
    prompt = ""

    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.sockfile = self.sock.makefile('r')
        self.field = Field_attributes()
        super().__init__()

        self.add_monster_type()

    def _send(self, msg):
        msg = (json.dumps(msg) + '\n').encode()
        self.sock.sendall(msg)
        response = self.sockfile.readline()
        if not response:
            raise ConnectionError("Server disconnected")
        return json.loads(response.strip())
    
    def _close(self):
        self.sockfile.close()
        self.sock.close()

    def player_moving(self, dx, dy):
        cmd = {'cmd': "move", 'dx': dx, 'dy': dy}
        ans = self._send(cmd)
        print(ans["msg0"])
        if 'name' in ans:
            name = ans['name']
            hello = ans['hello']
            if name in self.field.custom_monsters:
                monster = self.field.custom_monsters[name]
                print(cowsay.cowsay(hello, cowfile=monster))
            else:
                monster = name
                print(cowsay.cowsay(hello, cow=monster))

    def field_addmon(self, line):
        try:
            line = shlex.split(line)
        except ValueError:
            raise ValueError(INVALID_ARGS)

        if len(line) != 8:
            raise ValueError(INVALID_ARGS)

        if line[0] not in self.field.monsters and line[0] not in self.field.custom_monsters:
            raise ValueError(UNKNOWN_MONSTER)
        name = line[0]
        
        try:
            ind = line.index('hello')
            hello = line[ind + 1]
            del line[ind:ind + 2]
        except (IndexError, ValueError):
            raise ValueError(INVALID_ARGS)

        try:
            ind = line.index('hp')
            hp = line[ind + 1]
            if hp.isdigit() and int(hp) > 0:
                hp = int(hp)
            else:
                raise ValueError(INVALID_ARGS)
        except (IndexError, ValueError):
            raise ValueError(INVALID_ARGS)

        try:
            ind = line.index('coords')
            x = int(line[ind + 1])
            y = int(line[ind + 2])
            if not(0 <= x < self.field.size_x and 0 <= y < self.field.size_y):
                raise ValueError(INVALID_ARGS)
        except (IndexError, ValueError):
            raise ValueError(INVALID_ARGS)

        cmd = {
            "cmd": "addmon",
            "name": name,
            "hp": hp,
            "x": x,
            "y": y,
            "hello": hello
        }
        
        ans = self._send(cmd)
        print(ans["msg0"])
        if "msg1" in ans:
            print(ans["msg1"])

    def player_attack(self, line):
        args = shlex.split(line)
        if len(args) == 1:
            name = args[0]
            weapon = 'sword'
        elif len(args) == 3 and args[1] == 'with':
            name = args[0]
            weapon = args[2]
        else:
            print("Invalid arguments")
            return

        if weapon not in self.field.weapons:
            print("Unknown weapon")
            return
    
        cmd = {
            "cmd": "attack", 
            "name": name, 
            "weapon": weapon
        }
        ans = self._send(cmd)
        print(ans["msg0"])
        if "msg1" in ans:
            print(ans["msg1"])

    def add_monster_type(self):
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
    
        self.field.custom_monsters['jgsbat'] = jgsbat
        cmd = {
            "cmd": "new_custom_monster",
            "name": "jgsbat"
        }
        self._send(cmd)

    def do_down(self, arg):
        self.player_moving(0, 1)

    def do_up(self, arg):
        self.player_moving(0, -1)

    def do_left(self, arg):
        self.player_moving(-1, 0)

    def do_right(self, arg):
        self.player_moving(1, 0)

    def do_addmon(self, arg):
        try:
            self.field_addmon(arg)
        except ValueError as error:
            if error.args[0] == INVALID_ARGS:
                print("Invalid arguments")
            elif error.args[0] == UNKNOWN_MONSTER:
                print("Cannot add unknown monster")

    def do_attack(self, arg):
        self.player_attack(arg)
    
    def complete_attack(self, text, line, begidx, endidx):
        args = shlex.split(line)
        all_cows = list(self.field.custom_monsters.keys()) + self.field.monsters
        
        if len(args) == 1:
            return sorted(all_cows)
        
        if len(args) == 2 and not line.endswith(' '):
            return sorted([nm for nm in all_cows if nm.startswith(text)])
        
        if len(args) == 2 and line.endswith(' '):
            return ["with"]
        
        if len(args) == 3 and args[2] == "with" and line.endswith(' '):
            return list(self.field.weapons)
        
        if len(args) == 4 and args[2] == "with":
            return [w for w in self.field.weapons if w.startswith(text)]
        
        return []

    def emptyline(self):
        pass

    def default(self, line):
        if not line.strip():
            return
        print("Unknown command")
    
    def do_exit(self, arg):
        print("Goodbye")
        self._close()
        return True
    
    def do_EOF(self, arg):
        self._close()
        print("Goodbye")
        return True


if __name__ == '__main__':
    try:
        MUDClient(HOST, PORT).cmdloop()
    except ConnectionRefusedError:
        print(f"Cannot connect to {HOST}:{PORT}")