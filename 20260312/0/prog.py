import cmd
import shlex
from pathlib import Path


class SizeCmdl(cmd.Cmd):
    PROMPT = "==> "

    def do_size(self, args):
        """Print file sizes"""

        args = shlex.split(args)
        for name in args:
            print(f"{name}: {Path(name).stat().st_size}")


    def complete_size(self, text, line, begidx, endidx)
        return [str(p) for p in Path("").parent.glob(f"{text}")]


    def do_exit(self, arg):
        """Выход"""
        return True

    def do_EOF(self, arg):
        print()
        return True



if __name__ == '__main__':
    SizeCmdl().cmdloop()

