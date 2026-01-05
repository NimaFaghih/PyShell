import os
import sys
from .readline_setup import readline


def completer(shell, text, state):
    """Tab completion for commands and files; designed to be called by readline."""
    if state == 0:
        try:
            begin_idx = readline.get_begidx()
        except Exception:
            begin_idx = 0

        if begin_idx == 0:
            shell._completion_matches = complete_command(shell, text)
        else:
            shell._completion_matches = complete_path(text)

    if state < len(getattr(shell, '_completion_matches', [])):
        match = shell._completion_matches[state]
        if os.path.isdir(match) and not match.endswith('/'):
            return match + '/'
        return match
    return None


def complete_command(shell, text):
    """Complete command names"""
    builtins = ['cd', 'pwd', 'echo', 'exit', 'export', 'unset', 'history', 'type', 'ls', 'cat', 'clear']

    commands = set(builtins)
    path_sep = ';' if sys.platform == 'win32' else ':'
    path_dirs = os.environ.get('PATH', '').split(path_sep)

    for directory in path_dirs:
        if os.path.isdir(directory):
            try:
                for f in os.listdir(directory):
                    full_path = os.path.join(directory, f)
                    if os.path.isfile(full_path):
                        if sys.platform == 'win32':
                            if any(f.lower().endswith(ext) for ext in ['.exe', '.bat', '.cmd', '.com']):
                                name = os.path.splitext(f)[0] if f.lower().endswith('.exe') else f
                                commands.add(name)
                        elif os.access(full_path, os.X_OK):
                            commands.add(f)
            except Exception:
                pass

    return sorted([cmd for cmd in commands if cmd.startswith(text)])


def complete_path(text):
    """Complete file and directory paths"""
    if not text:
        text = '.'

    dirname = os.path.dirname(text) or '.'
    basename = os.path.basename(text)

    try:
        entries = os.listdir(dirname)
        matches = []
        for e in entries:
            if e.startswith(basename) or (not basename and e):
                full_path = os.path.join(dirname, e)
                matches.append(full_path)

        return sorted(matches)
    except Exception:
        return []
