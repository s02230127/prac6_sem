"""Entry point for MUD client."""

import sys
from .mud_client import MUDClient
from ..common.constants import HOST, PORT


def main():
    """Run MUD client."""
    print("<<< Welcome to Python-MUD 0.1 >>>")
    try:
        if len(sys.argv) < 2:
            print("Error. No name")
            sys.exit(0)
        name = sys.argv[1]

        MUDClient(HOST, PORT, name).cmdloop()
    except ConnectionRefusedError:
        print(f"Cannot connect to {HOST}:{PORT}")
    except ValueError as error:
        print(error)


if __name__ == '__main__':
    main()
