'''Single entry point for Ace Combat Wizard: launches the GUI by default, or
the Qt-free CLI when invoked with --cli as the first argument.

The mode is picked by that argument, not by how the file is run (double-
click, `python gui_main.py`, etc. all behave the same without --cli). Qt is
only ever imported inside the GUI branch below - never at module load time -
so `--cli` usage never touches PySide6, letting the CLI run in any plain
Python environment.'''
import sys


def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--cli':
        from cli import main as cli_main
        cli_main(sys.argv[2:])
    else:
        from gui.app import main as gui_main
        gui_main()


if __name__ == '__main__':
    main()
