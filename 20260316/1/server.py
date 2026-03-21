import asyncio
import cowsay


HOST = "localhost"
PORT = 7778

SIZE_X = 10
SIZE_Y = 10
START_X = 0
START_Y = 0

class Field:
    def __init__(self, size_x=10, size_y=10, start_x=0, start_y=0):
        self.player = (start_x % size_x, start_y % size_y)
        self.monsters = {}
        self.monster_types = []
        self.weapons = {}
        self.size_x = size_x
        self.size_y = size_y


class MUDServer:
    def __init__(self):
        self.field = Field(SIZE_X, SIZE_Y, START_X, START_Y)
        
    def command_handler(self, data):
        data = data.decode().strip().split()
        cmd = data[0]
        msg = ''
        if cmd == 'move':
            x = (int(data[1]) + self.field.player[0]) % self.field.size_x
            y = (int(data[2]) + self.field.player[1]) % self.field.size_y
            self.field.player = (x, y)
            msg += f"Moved to ({x}, {y})"
            if self.field.player in self.field.monsters:
                msg += '\t' + self.field.monsters[(x, y)]['name'] + '\t' + self.field.monsters[(x, y)]['hello']
                
        elif cmd == 'get_monsters':
            msg = '\t'.join(cowsay.list_cows() + list(self.field.monster_types))
        
        elif cmd == 'new_custom_monster':
            self.field.monster_types.append(data[1])
            msg = '0'
        
        elif cmd == 'addmon':
            name = data[1]
            hp = int(data[2])
            x, y = int(data[3]), int(data[4])
            hello = ' '.join(data[5:])
            stats = {
                'name': name,
                'hello': hello,
                'hp': hp
            }
            fl_replaced = (x, y) in self.field.monsters
            self.field.monsters[(x, y)] = stats
            msg = f"Added monster {stats['name']} to ({x}, {y}) saying {stats['hello']}"
            if fl_replaced:
                msg = "Replaced the old monster" + '\t' + msg        
        msg += '\n'
        return msg
        
        
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
            writer.close()
            await writer.wait_closed()
        finally:
            print(f"Client disconnected: {addr}")
            writer.close()
            await writer.wait_closed()
    
    async def run(self, host, port):
        server = await asyncio.start_server(self.handle_client, host, port)
        async with server:
            await server.serve_forever()



if __name__ == '__main__':
    mud = MUDServer()
    asyncio.run(mud.run(HOST, PORT))
