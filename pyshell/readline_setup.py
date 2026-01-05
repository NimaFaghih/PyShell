import os
import atexit
try:
    import readline
    HAS_READLINE = True
except Exception:
    readline = None
    HAS_READLINE = False


def setup_readline(shell):
    """Configure readline for history and autocompletion"""
    if not HAS_READLINE:
        return

    if os.path.exists(shell.history_file):
        try:
            readline.read_history_file(shell.history_file)
        except Exception:
            pass

    readline.set_history_length(1000)

    atexit.register(lambda: save_history(shell))

    readline.set_completer(lambda text, state: shell.completer(text, state))
    try:
        readline.parse_and_bind("tab: complete")
    except Exception:
        pass

    try:
        readline.set_completer_delims(' \t\n;|&<>')
    except Exception:
        pass


def save_history(shell):
    """Save command history to file"""
    if HAS_READLINE and readline is not None:
        try:
            readline.write_history_file(shell.history_file)
        except Exception:
            pass
    else:
        try:
            with open(shell.history_file, 'w') as f:
                for cmd in getattr(shell, 'history', [])[-1000:]:
                    f.write(cmd + '\n')
        except Exception:
            pass
