import asyncio

def sqroots(coeffs:str) -> str:
    a, b, c = list(map(int, coeffs.split()))
    d = (b ** 2 - 4 * a * c)
    if a == 0:
        num = -c / b if b != 0 else ""

        return f"{num}"
    if d < 0:
        return ""
    elif d == 0:
        return str((-b + d ** 0.5) / ( 2 * a))
    else:
        mi, ma = sorted([(-b + d ** 0.5) / ( 2 * a), (-b - d ** 0.5) / ( 2 * a)])
        return f"{mi} {ma}"

'''
async def echo(reader, writer):
    while data := await reader.readline():
        res = data.strip().decode()
        try:
            data = sqroots(res)
            writer.write(f"{data}\n".encode())
        except Exception as error:
            writer.write(f"{error}\n".encode())
    writer.close()
    await writer.wait_closed()

async def main():
    server = await asyncio.start_server(echo, '0.0.0.0', 1337)
    async with server:
        await server.serve_forever()

asyncio.run(main())
'''

import sys
import socket


def sqrootnet(coeffs: str, s: socket.socket) -> str:
    s.sendall((coeffs + "\n").encode())
    return s.recv(128).decode().strip()

host = "localhost"
port = 1337
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((host, port))
    while msg := sys.stdin.buffer.readline():
        s.sendall(msg)
        print(s.recv(1024).rstrip().decode())
