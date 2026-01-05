# PyShell

A small, POSIX-style command-line shell implemented in Python for learning and experimentation. PyShell supports builtins, PATH-based external command lookup and execution, pipelines, I/O redirection, command history, and optional tab completion.

Table of Contents

- [Features](#features)
- [Quick Demo](#quick-demo)
- [Installation](#installation)
- [Running](#running)
- [Builtins & PATH lookup](#builtins--path-lookup)
- [Executing External Programs](#executing-external-programs)
- [Development](#development)
- [Testing](#testing)
- [CI / Linting](#ci--linting)
- [Contributing](#contributing)
- [License](#license)

## Implemented features & examples 

Below are the features implemented in this repository along with short, copy-pastable examples and pointers to the relevant modules/tests.

- **Builtins** (`pyshell/builtins.py`) — implemented: `cd`, `pwd`, `echo`, `exit`, `export`, `unset`, `history`, `type`, `ls`, `cat`, `clear`.

  - Change directory (handles missing dirs and permissions):
    ```sh
    cd /tmp
    cd does-not-exist   # -> prints error
    ```
  - Print working directory:
    ```sh
    pwd
    ```
  - Echo and redirection:
    ```sh
    echo hello
    echo hi > out.txt
    echo more >> out.txt
    ```
  - Environment and variable expansion:
    ```sh
    export NAME=Nima
    echo $NAME        # -> Nima
    unset NAME
    ```
  - History (works with `readline` if available):
    ```sh
    history
    ```
  - `type` builtin: reports builtins and searches `PATH` for executables
    ```sh
    type echo         # -> echo is a shell builtin
    type ls           # -> ls is /usr/bin/ls
    type invalid_cmd  # -> invalid_cmd: not found
    ```

- **External command execution**

  ```sh
  custom_exe arg1 arg2
  # If `custom_exe` is found in PATH, it is executed with argv ['<fullpath>', 'arg1', 'arg2']
  ```


- **Pipelines** (`|`) and **I/O redirection** (`>`, `>>`, `<`, `2>`) are supported. Examples:

  ```sh
  echo 'hello\nworld' | sed 's/world/planet/'
  cat < input.txt | grep something > out.txt
  somecmd 2> err.txt
  ```

- **Tokenization & variable expansion** — supports quoted tokens, escaping and `$VAR` and `$?` expansion:

  ```sh
  export FOO=bar
  echo "$FOO"
  echo $?          # exit status of last command
  ```

- **Tab completion & history** — when Python `readline` is available (or `pyreadline3` on Windows), tab-completion for commands and file paths and persistent history are enabled.

## Quick Demo

Run the shell and try the following:

```sh
$ python ./main.py
PyShell - A POSIX-compliant shell
Type 'exit' to quit

$ ls
$ pwd
$ echo hello
$ export NAME=Nima
$ echo $NAME
$ type ls
ls is /usr/bin/ls
$ custom_exe arg1 arg2   # runs custom_exe found in PATH
$ exit
```

## Installation

To enable tab completion on Windows, install `pyreadline3`:

```powershell
  pip install pyreadline3
```

## Running

- From project root:

```sh
python ./main.py
```