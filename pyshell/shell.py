import os
import signal
from .readline_setup import HAS_READLINE, setup_readline, save_history
from . import parsing
from . import completion
from . import execute


class Shell:
    def __init__(self):
        self.history_file = os.path.expanduser("~/.pyshell_history")
        self.prompt = "$ "
        self.last_exit_code = 0

        if HAS_READLINE:
            setup_readline(self)
        else:
            self.history = []

        self.setup_signal_handlers()

    def setup_signal_handlers(self):
        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, sig, frame):
        print("^C")

    def completer(self, text, state):
        return completion.completer(self, text, state)

    def tokenize(self, line):
        return parsing.tokenize(line)

    def expand_variables(self, tokens):
        return parsing.expand_variables(tokens, self)

    def parse_redirections(self, tokens):
        return parsing.parse_redirections(tokens)

    def execute_pipeline(self, commands):
        return execute.execute_pipeline(self, commands)

    def execute_command(self, cmd_line):
        try:
            return execute.execute_command(self, cmd_line)
        except SystemExit:
            raise

    def run(self):
        print("PyShell - A POSIX-compliant shell")
        print("Type 'exit' to quit")

        if HAS_READLINE:
            print("[+] Tab completion enabled (press Tab)")
            print("[+] Command history enabled (Up/Down arrows)")
        else:
            print("[-] readline not available - no Tab completion")
            print("  On Windows: pip install pyreadline3")
        print()

        while True:
            try:
                cwd = os.getcwd()
                home = os.path.expanduser('~')
                if cwd.startswith(home):
                    cwd = '~' + cwd[len(home):]

                self.prompt = f"{cwd} $ "

                line = input(self.prompt).strip()

                if not line:
                    continue

                if not HAS_READLINE:
                    self.history.append(line)

                if '|' in line:
                    commands = [cmd.strip() for cmd in line.split('|')]
                    self.last_exit_code = self.execute_pipeline(commands)
                else:
                    self.last_exit_code = self.execute_command(line)

            except EOFError:
                print()
                save_history(self)
                break
            except KeyboardInterrupt:
                print()
                continue
            except SystemExit:
                save_history(self)
                raise
            except Exception as e:
                print(f"Error: {e}")
                self.last_exit_code = 1

        save_history(self)

