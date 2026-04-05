"""Entry point for MUD server."""

import asyncio
from .mud_server import MUDServer
from ..common.constants import HOST, PORT


def main():
    """Run MUD server."""
    mud = MUDServer()
    asyncio.run(mud.run(HOST, PORT))


if __name__ == '__main__':
    main()
