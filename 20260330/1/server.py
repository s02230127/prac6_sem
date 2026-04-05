import asyncio
import cowsay
import json
from io import StringIO


HOST = "localhost"
PORT = 7779

SIZE_X = 10
SIZE_Y = 10
START_X = 0
START_Y = 0

class Field:
    def __init__(self, size_x=10, size_y=10, start_x=0, start_y=0):
        self.players = {}
        self.monsters = {}
        self.monster_types = []
        self.custom_monsters = {}
        self.size_x = size_x
        self.size_y = size_y
        self.weapons = {"sword": 10, "spear": 15, "axe": 20}

class Player:
    def __init__(self, name, writer, size_x=10, size_y=10, start_x=0, start_y=0):
        self.name = name
        self.writer = writer
        self.x = start_x % size_x
        self.y = start_y % size_y

class MUDServer:
    def __init__(self):
        self.field = Field(SIZE_X, SIZE_Y, START_X, START_Y)
        self.add_monster_type()

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

    def command_handler(self, player, data):
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
                name = self.field.monsters[(x, y)]['name'] 
                hello = self.field.monsters[(x, y)]['hello']
                if name in self.field.custom_monsters:
                    monster = self.field.custom_monsters[name]
                    msg += cowsay.cowsay(hello, cowfile=monster) + '\n'
                else:
                    monster = name
                    msg += cowsay.cowsay(hello, cow=monster) + '\n'
        
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
                msg  += f"{monster['name']} now has {monster['hp']}\n"

        elif cmd == 'sayall':
            text = data['msg']
            msg = f"{player.name}: {text}\n"
            return 'public', msg
        
        if msg_type == 'public':
            msg = player.name + ' ' + msg
        return msg_type, msg
    
    async def send_to(self, player, msg):
        data = msg.encode() + b'\0'
        player.writer.write(data)
        await player.writer.drain()

    async def broadcast(self, msg):
        data = msg.encode() + b'\0'
        players = list(self.field.players.values())
        for player in players:
            player.writer.write(data)
        for player in players:
            await player.writer.drain()

    async def handle_client(self, reader, writer):
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
        server = await asyncio.start_server(self.handle_client, host, port)
        print("Server is started")
        async with server:
            await server.serve_forever()


if __name__ == '__main__':
    mud = MUDServer()
    asyncio.run(mud.run(HOST, PORT))
