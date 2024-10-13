import re

def R_tokenizer(code):
    tokens = []
    token_specification = [
        ('NUMBER', r'\d+'),                 # Integer
        ('ID', r'[A-Za-z_]\w*'),            # Identifiers
        ('OP', r'[+\-*/=><!&|]+'),          # Operators, including logical operators
        ('PUNCT', r'[{}();,]'),             # Punctuation: braces, parentheses, semicolon, comma
        ('DOT', r'\.'),                     # Dot operator
        ('NEWLINE', r'\n'),                 # Line endings
        ('SKIP', r'[ \t]+'),                # Skip over spaces and tabs
        ('MISMATCH', r'.'),                 # Any other character
    ]
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    for mo in re.finditer(tok_regex, code):
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'NUMBER':
            value = int(value)
        elif kind in {'NEWLINE','SKIP'}:
            continue
        elif kind == 'MISMATCH':
            raise RuntimeError(f'{value!r} unexpected')
        tokens.append((kind, value))
    return tokens

