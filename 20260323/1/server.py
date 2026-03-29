import asyncio
import cowsay
import json

HOST = "localhost"
PORT = 7779

SIZE_X = 10
SIZE_Y = 10
START_X = 0
START_Y = 0

class Field:
    def __init__(self, size_x=10, size_y=10, start_x=0, start_y=0):
        self.player = (start_x % size_x, start_y % size_y)
        self.monsters = {}
        self.monster_types = []
        self.size_x = size_x
        self.size_y = size_y
        self.weapons = {"sword": 10, "spear": 15, "axe": 20}


class MUDServer:
    def __init__(self):
        self.field = Field(SIZE_X, SIZE_Y, START_X, START_Y)
        
    def command_handler(self, data):
        data = json.loads(data.decode().strip())

        cmd = data['cmd']
        ans = {}
        ind_msg = 0
        if cmd == 'move':
            x = (int(data['dx']) + self.field.player[0]) % self.field.size_x
            y = (int(data['dy']) + self.field.player[1]) % self.field.size_y
            self.field.player = (x, y)
            ans[f"msg{ind_msg}"] = f"Moved to ({x}, {y})"
            ind_msg += 1
            if self.field.player in self.field.monsters:
                ans['name'] = self.field.monsters[(x, y)]['name'] 
                ans['hello'] = self.field.monsters[(x, y)]['hello']
                
        elif cmd == 'new_custom_monster':
            self.field.monster_types.append(data['name'])
            ans['res'] = 0
        
        elif cmd == 'addmon':
            name = data['name']
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
            ans[f"msg{ind_msg}"] = f"Added monster {stats['name']} to ({x}, {y}) saying {stats['hello']}"
            ind_msg += 1
            if fl_replaced:
                ans[f"msg{ind_msg}"] = "Replaced the old monster"

        elif cmd == "attack":
            name = data['name']
            weapon = data['weapon']
            if self.field.player not in self.field.monsters:
                ans[f"msg{ind_msg}"] = f"No {name} here"
                return json.dumps(ans) + '\n'
        
            damage = self.field.weapons[weapon]
            monster = self.field.monsters[self.field.player]

            if monster['name'] != name:
                ans[f"msg{ind_msg}"] = f"No {name} here"
                return json.dumps(ans) + '\n'
            hp_before = monster['hp']
            hp_after = hp_before - damage if hp_before - damage >= 0 else 0

            ans[f"msg{ind_msg}"] = f"Attacked {monster['name']}, damage {hp_before - hp_after} hp"
            ind_msg += 1
            if hp_after == 0:
                del self.field.monsters[self.field.player]
                ans[f"msg{ind_msg}"] = f"{monster['name']} died"
            else:
                monster['hp'] = hp_after
                ans[f"msg{ind_msg}"] = f"{monster['name']} now has {monster['hp']}"
        return json.dumps(ans) + '\n'
        
    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        print(f"Client connected: {addr}")
        try:
            while True:
                data = await reader.readline()
                if not data:
                    break
                ans = self.command_handler(data)
                writer.write(ans.encode())
                await writer.drain()
        finally:
            print(f"Client disconnected: {addr}")
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
