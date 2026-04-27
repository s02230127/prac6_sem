"""MUD server."""

import os
import gettext
import asyncio
import cowsay
import json
import random
from io import StringIO

from .game_objects import Field, Player
from ..common.constants import SIZE_X, SIZE_Y, START_X, START_Y, SECONDS_FOR_WANDER
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


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

    def _get_translator(self, locale):
        """Returns translator."""
        if locale == 'ru_RU.UTF8':
            try:
                return gettext.translation(
                    'messages',
                    localedir=os.path.join(BASE_DIR, 'locales'),
                    languages=['ru']
                )
            except FileNotFoundError:
                return gettext.NullTranslations()
        return gettext.NullTranslations()

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
                if direct == "right":
                    msg_key = "{name} moved one cell right\n"
                elif direct == "left":
                    msg_key = "{name} moved one cell left\n"
                elif direct == "up":
                    msg_key = "{name} moved one cell up\n"
                else:
                    msg_key = "{name} moved one cell down\n"
                await self.broadcast([
                    ("msg", msg_key, {"name": monster["name"]})
                ])
                for player in self._players_on_cell(nx, ny):
                    await self.send_to(player, [
                        ("raw", self._cowsay_monster(monster))
                    ])
                return

    async def _wander_monsters(self):
        """Move monsters every 30 seconds."""
        while True:
            await asyncio.sleep(SECONDS_FOR_WANDER)
            if self.field.fl_movemonsters:
                await self._move_random_monster()

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
        parts = []
        if cmd == 'move':
            x = (int(data['dx']) + player.x) % self.field.size_x
            y = (int(data['dy']) + player.y) % self.field.size_y
            player.x = x
            player.y = y

            parts.append(
                ("msg", "Moved to ({x}, {y})\n", {"x": x, "y": y}),
            )
            if (x, y) in self.field.monsters:
                parts.append(
                    ("raw", self._cowsay_monster(self.field.monsters[(x, y)]))
                )
            return "private", parts

        elif cmd == 'addmon':
            name = data['name']
            if name not in cowsay.list_cows() and name not in self.field.custom_monsters:
                parts.append(
                    ("msg", "Cannot add unknown monster\n", {})
                )
                return "private", parts

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
            parts.append(
                (
                    "nmsg",
                    "{player} added monster {name} to ({x}, {y}) with {hp} hit point saying {hello}\n",
                    "{player} added monster {name} to ({x}, {y}) with {hp} hit points saying {hello}\n",
                    hp,
                    {
                        "name": stats["name"],
                        "x": x,
                        "y": y,
                        "hp": hp,
                        "hello": stats["hello"],
                        "player": player.name
                    }
                )
            )
            if fl_replaced:
                parts.append(
                    ("msg", "Replaced the old monster\n", {})
                )
            return "public", parts

        elif cmd == "attack":
            name = data['name']
            weapon = data['weapon']
            if (player.x, player.y) not in self.field.monsters:
                parts.append(
                    ("msg", "No {name} here\n", {"name": name})
                )
                return "private", parts

            damage = self.field.weapons[weapon]
            monster = self.field.monsters[(player.x, player.y)]

            if monster['name'] != name:
                parts.append(
                    ("msg", "No {name} here\n", {"name": name})
                )
                return "private", parts

            hp_before = monster['hp']
            hp_after = hp_before - damage if hp_before - damage >= 0 else 0
            dealt = hp_before - hp_after

            parts.append(
                (
                    "nmsg",
                    "{player} attacked {name} with {weapon}, damage {damage} hit point\n",
                    "{player} attacked {name} with {weapon}, damage {damage} hit points\n",
                    dealt,
                    {
                        "player": player.name,
                        "name": monster["name"],
                        "weapon": weapon,
                        "damage": dealt,
                    }
                )
            )

            if hp_after == 0:
                del self.field.monsters[(player.x, player.y)]
                parts.append(
                    ("msg", "{name} died\n", {"name": monster["name"]})
                )
            else:
                monster['hp'] = hp_after
                parts.append(
                    (
                        "nmsg",
                        "{name} now has {hp} hit point\n",
                        "{name} now has {hp} hit points\n",
                        hp_after,
                        {
                            "name": monster["name"],
                            "hp": hp_after,
                        }
                    )
                )
            return "public", parts

        elif cmd == 'sayall':
            text = data['msg']
            parts.append(
                ("raw", f"{player.name}: {text}\n")
            )
            return "public", parts

        elif cmd == 'movemonsters':
            state = data['state']
            if state == 'off':
                self.field.fl_movemonsters = False
                parts.append(
                    ("msg", "Moving monsters: off\n", {})
                )
            elif state == 'on':
                self.field.fl_movemonsters = True
                parts.append(
                    ("msg", "Moving monsters: on\n", {})
                )
            return "private", parts

        elif cmd == 'locale':
            locale = data['locale']
            player.locale = locale
            parts.append(
                ("msg", "Set up locale: {locale}\n", {"locale": locale})
            )
            return "private", parts

        return "private", [
            ("raw", "Unknown command\n")
        ]

    def _make_message(self, player, parts):
        """Build localized message from parts for one player."""
        translator = self._get_translator(player.locale)
        chunks = []

        for part in parts:
            kind = part[0]

            if kind == "msg":
                _, msg_key, kwargs = part
                text = translator.gettext(msg_key).format(**kwargs)
                chunks.append(text)

            elif kind == "nmsg":
                _, singular, plural, n, kwargs = part
                text = translator.ngettext(singular, plural, n).format(**kwargs)
                chunks.append(text)

            elif kind == "raw":
                _, text = part
                chunks.append(text)

        return "".join(chunks)

    async def send_to(self, player, parts):
        """Send localized message parts to one player."""
        data = self._make_message(player, parts).encode() + b'\0'
        player.writer.write(data)
        await player.writer.drain()

    async def broadcast(self, parts):
        """Broadcast localized message parts to all players."""
        players = list(self.field.players.values())

        for player in players:
            data = self._make_message(player, parts).encode() + b'\0'
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
            player_name = None
            if data['cmd'] == 'reg' and data['name'] not in self.field.players:
                player_name = data['name']
                player = Player(player_name, writer)
                self.field.players[player_name] = player
                msg = [
                    ("msg", "Successfully registered as {name}\n", {"name": player_name})
                ]
                await self.send_to(player, msg)

                await self.broadcast([
                    ("msg", "{name} joined the MUD\n", {"name": player_name})
                ])
                print(addr, "has taken name", player_name)
            else:
                writer.write("Registration denied: name already in use\n".encode() + b'\0')
                await writer.drain()
                raise ConnectionAbortedError

            while True:
                data = await reader.readline()
                if not data:
                    break
                ans_type, parts = self.command_handler(player, data)
                if ans_type == 'public':
                    await self.broadcast(parts)
                else:
                    await self.send_to(player, parts)
        except ConnectionAbortedError:
            pass
        finally:
            print(f"Client disconnected: {addr}")

            if player_name:
                del self.field.players[player_name]
                print(f"{player_name} left, name is avaible now")
                await self.broadcast([
                    ("msg", "{name} left the MUD\n", {"name": player_name})
                ])

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
