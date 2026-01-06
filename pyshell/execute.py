import subprocess
from . import parsing
from . import builtins


def execute_external(shell, tokens, stdin_redir, stdout_redir, stderr_redir, append):
    """Execute external command with redirections"""
    stdin = None
    stdout = None
    stderr = None
    
    if not tokens:
        return 1

    prog = tokens[0]
    full_path = builtins.find_executable(prog)
    if full_path is None:
        print(f"{prog}: command not found")
        return 127

    tokens = [full_path] + tokens[1:]

    try:
        if stdin_redir:
            stdin = open(stdin_redir, 'r')

        if stdout_redir:
            mode = 'a' if append else 'w'
            stdout = open(stdout_redir, mode)

        if stderr_redir:
            stderr = open(stderr_redir, 'w')

        result = subprocess.run(
            tokens,
            stdin=stdin,
            stdout=stdout,
            stderr=stderr
        )

        return result.returncode

    except FileNotFoundError:
        print(f"{tokens[0]}: command not found")
        return 127
    except Exception as e:
        print(f"Error: {e}")
        return 1
    finally:
        if stdin:
            stdin.close()
        if stdout:
            stdout.close()
        if stderr:
            stderr.close()


def execute_command(shell, cmd_line):
    """Execute a single command with redirections and builtins"""
    tokens = parsing.tokenize(cmd_line)
    if not tokens:
        return 0

    clean_tokens = []
    for token in tokens:
        if token.startswith('#'):
            break
        clean_tokens.append(token)

    if not clean_tokens:
        return 0

    tokens = parsing.expand_variables(clean_tokens, shell)
    tokens, stdin_redir, stdout_redir, stderr_redir, append = parsing.parse_redirections(tokens)

    if tokens is None:
        return 1

    if not tokens:
        return 0

    cmd = tokens[0]
    args = tokens[1:]

    if cmd == 'exit':
        exit_code = int(args[0]) if args else 0
        raise SystemExit(exit_code)
    elif cmd == 'cd':
        return builtins.builtin_cd(shell, args)
    elif cmd == 'pwd':
        return builtins.builtin_pwd(shell)
    elif cmd == 'echo':
        return builtins.builtin_echo(shell, args, stdout_redir, append)
    elif cmd == 'export':
        return builtins.builtin_export(shell, args)
    elif cmd == 'unset':
        return builtins.builtin_unset(shell, args)
    elif cmd == 'history':
        return builtins.builtin_history(shell)
    elif cmd == 'type':
        return builtins.builtin_type(shell, args)
    elif cmd == 'ls':
        return builtins.builtin_ls(shell, args, stdout_redir, append)
    elif cmd == 'cat':
        return builtins.builtin_cat(shell, args, stdout_redir, append)
    elif cmd == 'clear':
        return builtins.builtin_clear(shell)

    return execute_external(shell, tokens, stdin_redir, stdout_redir, stderr_redir, append)


def execute_pipeline(shell, commands):
    """Execute a pipeline of commands"""
    if len(commands) == 1:
        return execute_command(shell, commands[0])

    processes = []

    for i, cmd in enumerate(commands):
        tokens = parsing.tokenize(cmd)
        if not tokens:
            return 1

        clean_tokens = []
        for token in tokens:
            if token.startswith('#'):
                break
            clean_tokens.append(token)

        if not clean_tokens:
            return 1

        tokens = parsing.expand_variables(clean_tokens, shell)
        tokens, stdin_r, stdout_r, stderr_r, append = parsing.parse_redirections(tokens)

        if tokens is None:
            return 1
        
        if i == 0:
            stdin = subprocess.PIPE if stdin_r else None
        else:
            stdin = processes[i - 1].stdout
        
        if i == len(commands) - 1:
            stdout = subprocess.PIPE if stdout_r else None
        else:
            stdout = subprocess.PIPE

        try:
            prog = tokens[0]
            full_path = builtins.find_executable(prog)
            if full_path is None:
                print(f"{prog}: command not found")
                return 127
            tokens = [full_path] + tokens[1:]

            proc = subprocess.Popen(
                tokens,
                stdin=stdin,
                stdout=stdout,
                stderr=subprocess.PIPE
            )
            processes.append(proc)

            if i > 0:
                processes[i - 1].stdout.close()
        except FileNotFoundError:
            print(f"{tokens[0]}: command not found")
            return 127
        except Exception as e:
            print(f"Error: {e}")
            return 1

    for proc in processes:
        proc.wait()

    return processes[-1].returncode
