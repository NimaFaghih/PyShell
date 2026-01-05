import os


def tokenize(line: str):
    """Simple tokenizer - split on whitespace, respecting quotes"""
    tokens = []
    current = ""
    in_quote = None
    escaped = False

    for char in line:
        if escaped:
            current += char
            escaped = False
        elif char == '\\':
            escaped = True
        elif char in ('"', "'"):
            if in_quote == char:
                in_quote = None
            elif in_quote is None:
                in_quote = char
            else:
                current += char
        elif char in (' ', '\t') and in_quote is None:
            if current:
                tokens.append(current)
                current = ""
        else:
            current += char

    if current:
        tokens.append(current)

    return tokens


def expand_variables(tokens: list, shell):
    """Expand environment variables in tokens"""
    expanded = []
    for token in tokens:
        if '$' in token:
            parts = []
            i = 0
            while i < len(token):
                if token[i] == '$':
                    if i + 1 < len(token) and token[i + 1] == '?':
                        parts.append(str(getattr(shell, 'last_exit_code', 0)))
                        i += 2
                    else:
                        j = i + 1
                        while j < len(token) and (token[j].isalnum() or token[j] == '_'):
                            j += 1
                        var_name = token[i + 1:j]
                        parts.append(os.environ.get(var_name, ''))
                        i = j
                else:
                    parts.append(token[i])
                    i += 1
            expanded.append(''.join(parts))
        else:
            expanded.append(token)
    return expanded


def parse_redirections(tokens: list):
    """Parse and remove redirection operators from tokens"""
    stdin_redir = None
    stdout_redir = None
    stderr_redir = None
    append = False

    cleaned_tokens = []
    i = 0

    while i < len(tokens):
        token = tokens[i]

        if token == '<':
            if i + 1 < len(tokens):
                stdin_redir = tokens[i + 1]
                i += 2
            else:
                print("Syntax error: expected filename after '<'")
                return None, None, None, None, None
        elif token == '>':
            if i + 1 < len(tokens):
                stdout_redir = tokens[i + 1]
                append = False
                i += 2
            else:
                print("Syntax error: expected filename after '>'")
                return None, None, None, None, None
        elif token == '>>':
            if i + 1 < len(tokens):
                stdout_redir = tokens[i + 1]
                append = True
                i += 2
            else:
                print("Syntax error: expected filename after '>>'")
                return None, None, None, None, None
        elif token == '2>':
            if i + 1 < len(tokens):
                stderr_redir = tokens[i + 1]
                i += 2
            else:
                print("Syntax error: expected filename after '2>'")
                return None, None, None, None, None
        else:
            cleaned_tokens.append(token)
            i += 1

    return cleaned_tokens, stdin_redir, stdout_redir, stderr_redir, append
