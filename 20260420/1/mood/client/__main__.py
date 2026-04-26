"""Entry point for MUD client."""

import argparse
from .mud_client import MUDClient
from ..common.constants import HOST, PORT


def main():
    """Run MUD client."""
    print("<<< Welcome to Python-MUD 0.1 >>>")
    parser = argparse.ArgumentParser()
    parser.add_argument("name", help="Player name")
    parser.add_argument("--file", help="Command file (.mood)", default=None)
    args = parser.parse_args()

    try:
        client = MUDClient(HOST, PORT, args.name)
        if args.file:
            client.run_script(args.file)
        else:
            client.cmdloop()

    except ConnectionRefusedError:
        print(f"Cannot connect to {HOST}:{PORT}")
    except ValueError as error:
        print(error)


if __name__ == '__main__':
    main()
