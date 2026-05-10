"""MUD client."""

import socket
import cmd
import shlex
import cowsay
import json
import sys
import threading
import readline
import time
import webbrowser
from importlib.resources import files

from ..common.constants import INVALID_ARGS


class Field_attributes:
    """Field attributes."""

    def __init__(self):
        """Initialize attributes."""
        self.monsters = cowsay.list_cows()
        self.custom_monsters = ["jgsbat"]
        self.size_x = 10
        self.size_y = 10
        self.weapons = ["spear", "axe", "sword"]


class MUDClient(cmd.Cmd):
    """MUD client."""

    prompt = ""

    def __init__(self, host, port, name):
        """Initialize client."""
        super().__init__()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.print_lock = threading.Lock()
        self.sock.connect((host, port))
        self._register(name)
        self.field = Field_attributes()
        self.recv_thread = threading.Thread(target=self._receiver, daemon=True)
        self.recv_thread.start()

    def _register(self, name):
        """Register player."""
        cmd = {
            'cmd': "reg",
            'name': name
        }
        self._send(cmd)
        buf = b''
        rcv = b''
        while rcv != b'\0':
            rcv = self.sock.recv(1)
            buf += rcv
        msg = buf.decode()
        if msg.startswith("Registration denied"):
            print(msg, end='')
            self._close()
            sys.exit(0)
        else:
            print(buf.decode(), end='')

    def _send(self, msg):
        """Send message."""
        msg = (json.dumps(msg) + '\n').encode()
        self.sock.sendall(msg)

    def _receiver(self):
        """Receive messages."""
        buf = b''
        try:
            while True:
                while b'\0' not in buf:
                    rcv = self.sock.recv(4096)
                    if not rcv:
                        return
                    buf += rcv
                msg, buf = buf.split(b'\0', maxsplit=1)
                with self.print_lock:
                    if readline.get_line_buffer():
                        print()
                    print(msg.decode(), end='')
                    print(readline.get_line_buffer(), end='', flush=True)
        except OSError:
            pass

    def _close(self):
        """Close connection."""
        self.sock.close()

    def run_script(self, filename):
        """Run commands from a file."""
        try:
            with open(filename, 'r') as file:
                for line in file:
                    line = line.strip()
                    if not line:
                        continue
                    self.onecmd(line)
                    time.sleep(1)
        except FileNotFoundError:
            print("File not found")
        finally:
            self._close()

    def player_moving(self, dx, dy):
        """Move player."""
        cmd = {'cmd': "move", 'dx': dx, 'dy': dy}
        self._send(cmd)

    def field_addmon(self, line):
        """Add monster."""
        try:
            line = shlex.split(line)
        except ValueError:
            raise ValueError(INVALID_ARGS)

        if len(line) != 8:
            raise ValueError(INVALID_ARGS)
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
            if not (0 <= x < self.field.size_x and 0 <= y < self.field.size_y):
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

        self._send(cmd)

    def player_attack(self, line):
        """Attack monster."""
        args = shlex.split(line)
        if len(args) == 1:
            name = args[0]
            weapon = 'sword'
        elif len(args) == 3 and args[1] == 'with':
            name = args[0]
            weapon = args[2]
        else:
            with self.print_lock:
                print("Invalid arguments")
            return

        if weapon not in self.field.weapons:
            with self.print_lock:
                print("Unknown weapon")
            return

        cmd = {
            "cmd": "attack",
            "name": name,
            "weapon": weapon
        }
        self._send(cmd)

    def sayall(self, line):
        """Send message to all."""
        try:
            args = shlex.split(line)
        except ValueError:
            raise ValueError(INVALID_ARGS)

        if len(args) != 1:
            raise ValueError(INVALID_ARGS)

        cmd = {
            'cmd': 'sayall',
            'msg': args[0]
        }
        self._send(cmd)

    def movemonsters(self, line):
        """Turn on/off monsters random moving."""
        try:
            args = shlex.split(line)
        except ValueError:
            raise ValueError(INVALID_ARGS)

        if len(args) != 1 or args[0] not in ('on', 'off'):
            raise ValueError(INVALID_ARGS)

        cmd = {
            'cmd': 'movemonsters',
            'state': args[0]
        }
        self._send(cmd)

    def locale(self, line):
        """Set locale."""
        try:
            args = shlex.split(line)
        except ValueError:
            raise ValueError(INVALID_ARGS)

        if len(args) != 1:
            raise ValueError(INVALID_ARGS)

        cmd = {
            'cmd': 'locale',
            'locale': args[0]
        }
        self._send(cmd)

    def do_down(self, arg):
        """Move down."""
        self.player_moving(0, 1)

    def do_up(self, arg):
        """Move up."""
        self.player_moving(0, -1)

    def do_left(self, arg):
        """Move left."""
        self.player_moving(-1, 0)

    def do_right(self, arg):
        """Move right."""
        self.player_moving(1, 0)

    def do_addmon(self, arg):
        """Add monster."""
        try:
            self.field_addmon(arg)
        except ValueError as error:
            with self.print_lock:
                if error.args[0] == INVALID_ARGS:
                    print("Invalid arguments")

    def do_sayall(self, line):
        """Say to all."""
        try:
            self.sayall(line)
        except ValueError as error:
            with self.print_lock:
                if error.args[0] == INVALID_ARGS:
                    print("Invalid arguments")

    def do_movemonsters(self, line):
        """Turn on/off monster moving."""
        try:
            self.movemonsters(line)
        except ValueError as error:
            with self.print_lock:
                if error.args[0] == INVALID_ARGS:
                    print("Invalid arguments")

    def do_locale(self, line):
        """Set locale."""
        try:
            self.locale(line)
        except ValueError as error:
            with self.print_lock:
                if error.args[0] == INVALID_ARGS:
                    print("Invalid arguments")

    def do_attack(self, arg):
        """Attack."""
        self.player_attack(arg)

    def complete_attack(self, text, line, begidx, endidx):
        """Autocomplete attack."""
        args = shlex.split(line)
        all_cows = self.field.custom_monsters + self.field.monsters

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

    def do_documentation(self, arg):
        """Open generated documentation in browser."""
        index = files("mood").joinpath("docs/html/index.html")
        webbrowser.open(index.as_uri())

    def emptyline(self):
        """Handle empty line."""
        pass

    def default(self, line):
        """Handle unknown command."""
        if not line.strip():
            return
        with self.print_lock:
            print("Unknown command")

    def do_exit(self, arg):
        """Exit game."""
        with self.print_lock:
            print("Goodbye")
        self._close()
        return True

    def do_EOF(self, arg):
        """Handle EOF."""
        with self.print_lock:
            print("Goodbye")
        self._close()
        return True
