import json
import socket
import time
import unittest
import multiprocessing

from mood.server.__main__ import main_server as run_server
from mood.common.constants import HOST, PORT


class TestMudServer(unittest.TestCase):
    def setUp(self):
        self.proc = multiprocessing.Process(target=run_server)
        self.proc.start()
        time.sleep(1)

        self.sock = socket.create_connection((HOST, PORT))
        self.sock.settimeout(2)

        self.buf = b''
        self.send({"cmd": "reg", "name": "tester"})
        self.recv_msg()
        self.recv_msg()

        self.send({"cmd": "movemonsters", "state": "off"})
        msg = self.recv_msg()
        self.assertEqual("Moving monsters: off\n", msg)

    def test_1_add_go_meet_attack(self):
        """Add monster, go to monster, meet monster, attack monster"""
        self.send({
            "cmd": "addmon",
            "name": "sheep",
            "hp": 35,
            "x": 1,
            "y": 1,
            "hello": "hello",
        })

        msg = self.recv_msg()
        self.assertEqual("tester added monster sheep to (1, 1) with 35 hit points saying hello\n", msg)

        cmd = {'cmd': "move", 'dx': 0, 'dy': 1}
        self.send(cmd)
        msg = self.recv_msg()
        self.assertEqual("Moved to (0, 1)\n", msg)

        cmd = {'cmd': "move", 'dx': 1, 'dy': 0}
        self.send(cmd)
        msg = self.recv_msg()
        ans = r'''Moved to (1, 1)
 _______ 
< hello >
 ------- 
  \
   \
       __     
      UooU\.'@@@@@@`.
      \__/(@@@@@@@@@@)
           (@@@@@@@@)
           `YY~~~~YY'
            ||    ||
'''

        self.assertEqual(ans, msg)

        cmd = {
            "cmd": "attack",
            "name": "sheep",
            "weapon": "sword"
        }
        self.send(cmd)
        msg = self.recv_msg()
        self.assertEqual("tester attacked sheep with sword, damage 10 hit points\nsheep now has 25 hit points\n", msg)

        cmd = {
            "cmd": "attack",
            "name": "sheep",
            "weapon": "axe"
        }
        self.send(cmd)
        msg = self.recv_msg()
        self.assertEqual("tester attacked sheep with axe, damage 20 hit points\nsheep now has 5 hit points\n", msg)

        cmd = {
            "cmd": "attack",
            "name": "sheep",
            "weapon": "spear"
        }
        self.send(cmd)
        msg = self.recv_msg()
        self.assertEqual("tester attacked sheep with spear, damage 5 hit points\nsheep died\n", msg)

        cmd = {
            "cmd": "attack",
            "name": "sheep",
            "weapon": "spear"
        }
        self.send(cmd)
        msg = self.recv_msg()
        self.assertEqual("No sheep here\n", msg)


    def tearDown(self):
        self.sock.close()
        self.proc.terminate()
        self.proc.join()

    def send(self, obj):
        data = json.dumps(obj) + "\n"
        self.sock.sendall(data.encode())

    def recv_msg(self):
        while b'\0' not in self.buf:
            rcv = self.sock.recv(4096)
            if not rcv:
                return ''
            self.buf += rcv

        msg, self.buf = self.buf.split(b'\0', maxsplit=1)
        return msg.decode()
        



if __name__ == "__main__":
    unittest.main()