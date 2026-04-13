"""MUD server."""

import asyncio
import cowsay
import json
import random
from io import StringIO

from .game_objects import Field, Player
from ..common.constants import SIZE_X, SIZE_Y, START_X, START_Y, SECONDS_FOR_WANDER


class MUDServer:
    """MUD server."""

    def __init__(self):
        """Initialize server."""
        self.field = Field(SIZE_X, SIZE_Y, START_X, START_Y)
        self.add_monster_type()
        self._wander_task = None

    def _cowsay_monster(self, monster):
        """Return cowsay monster message."""
        name = monster['name']
        hello = monster['hello']
        if name in self.field.custom_monsters:
            return cowsay.cowsay(hello, cowfile=self.field.custom_monsters[name]) + '\n'
        else:
            return cowsay.cowsay(hello, cow=name) + '\n'
        
    def _players_on_cell(self, x, y):
        """Returns players on cell."""
        players = []
        for player in self.field.players.values():
            if (player.x, player.y) == (x, y):
                players.append(player)
        return players

    async def _move_random_monster(self):
        """Move random monster."""
        if not self.field.monsters:
            return

        directions = [(1, 0, 'right'), (-1, 0, 'left'), (0, -1, 'up'), (0, 1, 'down')]
        monster_positions = list(self.field.monsters.keys())

        for _ in range(1000):
            x, y = random.choice(monster_positions)
            dx, dy, direct = random.choice(directions)
            nx = (x + dx) % self.field.size_x
            ny = (y + dy) % self.field.size_y
            if (nx, ny) not in self.field.monsters:
                monster = self.field.monsters.pop((x, y))
                self.field.monsters[(nx, ny)] = monster
                await self.broadcast(f"{monster['name']} moved one cell {direct}\n")
                for player in self._players_on_cell(nx, ny):
                    msg = self._cowsay_monster(monster)
                    await self.send_to(player, msg)
                return

    async def _wander_monsters(self):
        """Move monsters every 30 seconds."""
        await asyncio.sleep(SECONDS_FOR_WANDER)
        while True:
            await self._move_random_monster()
            await asyncio.sleep(SECONDS_FOR_WANDER)


    def add_monster_type(self):
        """Add custom monsters."""
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

    def command_handler(self, player, data):
        """Handle commands."""
        data = json.loads(data.decode().strip())

        cmd = data['cmd']
        msg = ""
        msg_type = "public"
        if cmd == 'move':
            x = (int(data['dx']) + player.x) % self.field.size_x
            y = (int(data['dy']) + player.y) % self.field.size_y
            player.x = x
            player.y = y
            msg += f"Moved to ({x}, {y})\n"
            msg_type = "private"
            if (x, y) in self.field.monsters:
                msg += self._cowsay_monster(self.field.monsters[(x, y)])

        elif cmd == 'addmon':
            name = data['name']

            if name not in cowsay.list_cows() and name not in self.field.custom_monsters:
                msg += "Cannot add unknown monster\n"
                return "private", msg

            hp = int(data['hp'])
            x, y = int(data['x']), int(data['y'])
            hello = data['hello']
            stats = {
                'name': name,
                'hello': hello,
                'hp': hp
            }
            fl_replaced = (x, y) in self.field.monsters
            self.field.monsters[(x, y)] = stats
            msg += f"added monster {stats['name']} to ({x}, {y}) with {hp} saying {stats['hello']}\n"
            if fl_replaced:
                msg += "Replaced the old monster\n"

        elif cmd == "attack":
            name = data['name']
            weapon = data['weapon']
            if (player.x, player.y) not in self.field.monsters:
                msg = f"No {name} here"
                return "private", msg

            damage = self.field.weapons[weapon]
            monster = self.field.monsters[(player.x, player.y)]

            if monster['name'] != name:
                msg = f"No {name} here"
                return "private", msg
            hp_before = monster['hp']
            hp_after = hp_before - damage if hp_before - damage >= 0 else 0

            msg += f"attacked {monster['name']} with {weapon}, damage {hp_before - hp_after} hp\n"
            if hp_after == 0:
                del self.field.monsters[(player.x, player.y)]
                msg += f"{monster['name']} died\n"
            else:
                monster['hp'] = hp_after
                msg += f"{monster['name']} now has {monster['hp']}\n"

        elif cmd == 'sayall':
            text = data['msg']
            msg = f"{player.name}: {text}\n"
            return 'public', msg

        if msg_type == 'public':
            msg = player.name + ' ' + msg
        return msg_type, msg

    async def send_to(self, player, msg):
        """Send to player."""
        data = msg.encode() + b'\0'
        player.writer.write(data)
        await player.writer.drain()

    async def broadcast(self, msg):
        """Broadcast message."""
        data = msg.encode() + b'\0'
        players = list(self.field.players.values())
        for player in players:
            player.writer.write(data)
        for player in players:
            await player.writer.drain()

    async def handle_client(self, reader, writer):
        """Handle client."""
        addr = writer.get_extra_info('peername')
        print(f"Client connected: {addr}")
        try:
            data = await reader.readline()
            if not data:
                return
            data = json.loads(data.decode().strip())
            msg = b''
            player_name = None
            if data['cmd'] == 'reg' and data['name'] not in self.field.players:
                player_name = data['name']
                player = Player(player_name, writer)
                self.field.players[player_name] = player
                msg = f"Successfully registered as {player_name}\n"
                await self.send_to(player, msg)
                await self.broadcast(f"{player_name} joined the MUD\n")
                print(addr, "has taken name", player_name)
            else:
                writer.write("Registration denied: name already in use\n".encode() + b'\0')
                await writer.drain()
                raise ConnectionAbortedError

            while True:
                data = await reader.readline()
                if not data:
                    break
                ans_type, ans = self.command_handler(player, data)
                if ans_type == 'public':
                    await self.broadcast(ans)
                else:
                    await self.send_to(player, ans)
        except ConnectionAbortedError:
            pass
        finally:
            print(f"Client disconnected: {addr}")

            if player_name:
                del self.field.players[player_name]
                print(f"{player_name} left, name is avaible now")
                await self.broadcast(f"{player_name} left the MUD\n")

            writer.close()
            await writer.wait_closed()

    async def run(self, host, port):
        """Run server."""
        server = await asyncio.start_server(self.handle_client, host, port)
        self._wander_task = asyncio.create_task(self._wander_monsters())
        print("Server is started")

        async with server:
            await server.serve_forever()

        if self._wander_task is not None:
            self._wander_task.cancel()
        
