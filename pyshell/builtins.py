import os
import sys
from .readline_setup import HAS_READLINE, readline


def builtin_cd(shell, args):
    """Change directory"""
    if not args:
        target = os.path.expanduser('~')
    else:
        target = os.path.expanduser(args[0])

    try:
        os.chdir(target)
        return 0
    except FileNotFoundError:
        print(f"cd: {target}: No such file or directory")
        return 1
    except PermissionError:
        print(f"cd: {target}: Permission denied")
        return 1
    except Exception as e:
        print(f"cd: {e}")
        return 1


def builtin_pwd(shell):
    """Print working directory"""
    print(os.getcwd())
    return 0


def builtin_echo(shell, args, stdout_redir=None, append=False):
    """Echo arguments"""
    output = ' '.join(args)

    if stdout_redir:
        try:
            mode = 'a' if append else 'w'
            with open(stdout_redir, mode) as f:
                f.write(output + '\n')
        except Exception as e:
            print(f"echo: {e}")
            return 1
    else:
        print(output)

    return 0


def builtin_export(shell, args):
    """Export environment variables"""
    for arg in args:
        if '=' in arg:
            key, value = arg.split('=', 1)
            os.environ[key] = value
        else:
            if arg in os.environ:
                pass  
            else:
                os.environ[arg] = ''
    return 0


def builtin_unset(shell, args):
    """Unset environment variables"""
    for arg in args:
        if arg in os.environ:
            del os.environ[arg]
    return 0


def builtin_history(shell):
    """Show command history"""
    if HAS_READLINE and readline is not None:
        for i in range(1, readline.get_current_history_length() + 1):
            print(f"{i:5d}  {readline.get_history_item(i)}")
    else:
        for i, cmd in enumerate(getattr(shell, 'history', []), 1):
            print(f"{i:5d}  {cmd}")
    return 0


def builtin_ls(shell, args, stdout_redir=None, append=False):
    """List directory contents (cross-platform)"""
    try:
        show_all = '-a' in args
        long_format = '-l' in args

        paths = [arg for arg in args if not arg.startswith('-')]
        target = paths[0] if paths else '.'

        entries = os.listdir(target)

        if not show_all:
            entries = [e for e in entries if not e.startswith('.')]

        entries.sort()

        if long_format:
            output = []
            for entry in entries:
                full_path = os.path.join(target, entry)
                try:
                    stat_info = os.stat(full_path)
                    size = stat_info.st_size
                    is_dir = 'd' if os.path.isdir(full_path) else '-'
                    output.append(f"{is_dir}  {size:>10}  {entry}")
                except Exception:
                    output.append(f"-  {'?':>10}  {entry}")
            result = '\n'.join(output)
        else:
            result = '  '.join(entries)

        if stdout_redir:
            mode = 'a' if append else 'w'
            with open(stdout_redir, mode) as f:
                f.write(result + '\n')
        else:
            print(result)

        return 0
    except FileNotFoundError:
        print(f"ls: {target}: No such file or directory")
        return 1
    except PermissionError:
        print(f"ls: {target}: Permission denied")
        return 1
    except Exception as e:
        print(f"ls: {e}")
        return 1


def builtin_cat(shell, args, stdout_redir=None, append=False):
    """Concatenate and print files"""
    if not args:
        print("cat: usage: cat file...")
        return 1

    try:
        output = []
        for filename in args:
            with open(filename, 'r') as f:
                output.append(f.read())

        result = ''.join(output)

        if stdout_redir:
            mode = 'a' if append else 'w'
            with open(stdout_redir, mode) as f:
                f.write(result)
        else:
            print(result, end='')

        return 0
    except FileNotFoundError as e:
        print(f"cat: {e.filename}: No such file or directory")
        return 1
    except Exception as e:
        print(f"cat: {e}")
        return 1


def builtin_clear(shell):
    """Clear the screen"""
    if sys.platform == 'win32':
        os.system('cls')
    else:
        os.system('clear')
    return 0


def find_executable(name: str):
    """Find an executable in PATH.
       Returns the full path to the executable if found and executable, otherwise None.
    """
    path_sep = ';' if sys.platform == 'win32' else ':'
    path_dirs = os.environ.get('PATH', '').split(path_sep)

    if sys.platform == 'win32':
        pathext = os.environ.get('PATHEXT', '.COM;.EXE;.BAT;.CMD')
        exts = [e.lower() for e in pathext.split(';') if e]

    for directory in path_dirs:
        if not directory:
            directory = os.getcwd()

        cmd_path = os.path.join(directory, name)

        if sys.platform == 'win32':
            _, ext = os.path.splitext(name)
            if ext:
                full_path = cmd_path
                if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                    return full_path
            else:
                for e in exts:
                    full_path = cmd_path + e
                    if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                        return full_path
        else:
            if os.path.isfile(cmd_path) and os.access(cmd_path, os.X_OK):
                return cmd_path

    return None


def builtin_type(shell, args):
    """Show command type"""
    if not args:
        print("type: usage: type command")
        return 1

    builtins = ['cd', 'pwd', 'echo', 'exit', 'export', 'unset', 'history', 'type', 'ls', 'cat', 'clear']

    for cmd in args:
        if cmd in builtins:
            print(f"{cmd} is a shell builtin")
            continue

        found_path = find_executable(cmd)
        if found_path:
            print(f"{cmd} is {found_path}")
        else:
            print(f"{cmd}: not found")
            return 1

    return 0
