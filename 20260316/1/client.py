import socket
import sys
import cmd

HOST = "localhost"
PORT = 7778

class MUDCLient(cmd.Cmd):
    intro = "<<< Welcome to Python-MUD 0.1 >>>"
    prompt = ""

    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.sockfile = self.sock.makefile('r')
        self._monster_names = None
        self._custom_cows = {}
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
        print(ans)

    def do_down(self, arg):
        self.player_moving(0, 1)

    def do_up(self, arg):
        self.player_moving(0, -1)

    def do_left(self, arg):
        self.player_moving(-1, 0)

    def do_right(self, arg):
        self.player_moving(1, 0)

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