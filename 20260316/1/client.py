import socket
import sys
import cmd
import shlex
import cowsay

HOST = "localhost"
PORT = 7778

UNKNOWN_MONSTER = 1
INVALID_ARGS = 2


class Field_attributes:
    def __init__(self):
        self.monsters = cowsay.list_cows()
        self.custom__monsters = {}
        self.size_x = 10
        self.size_y = 10
        self.weapons = ["weapon", "axe", "sword"]

class MUDCLient(cmd.Cmd):
    intro = "<<< Welcome to Python-MUD 0.1 >>>"
    prompt = ""

    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.sockfile = self.sock.makefile('r')
        self.field = Field_attributes()
        super().__init__()


    def _send(self, msg):
        self.sock.sendall(msg.encode())
        response = self.sockfile.readline()
        if not response:
            raise ConnectionError("Server disconnected")
        return response.strip()
    
    def _close(self):
        self.sockfile.close()
        self.sock.close()



    def player_moving(self, dx, dy):
        cmd = "move " + str(dx) + " " + str(dy) + '\n'
        ans = self._send(cmd)
        if '\t' in ans:
            ans = ans.split('\t', maxsplit=2)
            name = ans[1]
            hello = ans[2]
            if name in self.field.custom__monsters:
                monster = self.field.custom__monsters[name]
                print(cowsay.cowsay(hello, cowfile=monster))
            else:
                monster = name
                print(cowsay.cowsay(hello, cow=monster))
        else:
            print(ans)

    def field_addmon(self, line):
        try:
            line = shlex.split(line)
        except ValueError:
            raise ValueError(INVALID_ARGS)

        if len(line) != 8:
            raise ValueError(INVALID_ARGS)

        if line[0] not in self.field.monsters and line[0] not in self.field.custom__monsters:
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

        cmd = f"addmon {name} {hp} {x} {y} {hello}\n"
        ans = self._send(cmd)
        if ans.startswith("Replaced the old monster"):
            ans = ans.split('\t', maxsplit=1)
            print(ans[1])
            print(ans[0])
        else:
            print(ans)

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
        MUDCLient(HOST, PORT).cmdloop()
    except ConnectionRefusedError:
        print(f"Cannot connect to {HOST}:{PORT}")