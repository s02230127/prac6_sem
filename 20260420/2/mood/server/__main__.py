"""Entry point for MUD server."""

import asyncio
from .mud_server import MUDServer
from ..common.constants import HOST, PORT


def main_server(host=HOST, port=PORT):
    """Run MUD server."""
    mud = MUDServer()
    asyncio.run(mud.run(host, port))


if __name__ == '__main__':
    main_server()
