from pyshell.shell import Shell
import sys

if __name__ == "__main__":
    shell = Shell()
    try:
        shell.run()
    except SystemExit as e:
        sys.exit(int(getattr(e, 'code', 0) or 0))