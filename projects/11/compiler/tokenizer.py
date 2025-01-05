
import re
import logging
from dataclasses import dataclass

@dataclass
class Token:
    value: str
    type: str

# token catagories
KEYWORD = 'keyword'
SYMBOL = 'symbol'
INT_CONST = 'integerConstant'
STRING_CONST = 'stringConstant'
IDENTIFIER = 'identifier'

class TokenException(Exception):
    def __init__(self, msg):
        super().__init__(f"Tokenizer Error {msg}")


# definations for tokens catagaries
token_catagories = {
    KEYWORD: ['class', 'constructor', 'function', 'method',
                'field', 'static', 'var', 'int', 'char', 'boolean',
                'void', 'true', 'false', 'null', 'this', 'let', 'do',
                'if', 'else', 'while', 'return'],
    SYMBOL: ['{', '}', '(', ')', '[', ']','.',',',';','+','-', '*',
               '/', '&','|','<','>','=','~'],
    INT_CONST: r'[0-9]+',
    IDENTIFIER: r'[A-Za-z_](\w)*'
}

def identify_token_from_cats(token: str, catagories: tuple):
    for token_cat in catagories:
        token_ptrn = token_catagories[token_cat]
        if type(token_ptrn) == list:
            if token in token_ptrn:
                return Token(token, token_cat)
        elif re.match(token_ptrn, token):
                return Token(token, token_cat)
    return None

def identify_token_from_all_cats(token: str):
    if token := identify_token_from_cats(token, token_catagories.keys()):
        return token
    raise TokenException(f"Invalid token {token}")


def iter_each_instruction(file):
    with open(file, "r") as fp:
        block_comment = False
        for line in fp:
            icurrent = line.strip()
            pending_chars = ""
            exp_type = 0
            for char in icurrent:
                if block_comment:
                    if pending_chars == "*":
                        if char == "/":
                            block_comment = False
                            pending_chars = ""
                            exp_type = 0
                    pending_chars = char
                    continue

                if pending_chars == "/":
                    if char == "/":
                       # This is a comment
                       break
                    elif char == "*":
                        pending_chars = ""
                        exp_type = 0
                        block_comment = True
                        continue
                    else:
                        # Finish processing previous chars
                        yield identify_token_from_cats(pending_chars, (SYMBOL,))
                        pending_chars = ""
                        exp_type = 0

                if exp_type == STRING_CONST: 
                    if char == "\"":
                        yield Token(pending_chars, STRING_CONST)
                        pending_chars = ""
                        exp_type = 0
                    else:
                        pending_chars += char
                    continue

                elif char == " ":
                    if pending_chars != "":
                        yield identify_token_from_all_cats(pending_chars)
                        pending_chars = ""
                        exp_type = 0
                    continue

                
                if pending_chars == "/":
                    continue

                if (token := identify_token_from_cats(char, (KEYWORD, SYMBOL,))):
                    # process any pending buffer before identifier
                    if pending_chars != "":
                        pending_token = identify_token_from_all_cats(pending_chars)
                        yield pending_token
                        pending_chars = "" 
                        exp_type = 0
                    if char in ("/"):
                        pending_chars = char
                    else:
                        yield token
                else:
                    # Not a symbol and keyword, must be integer
                    if pending_chars == "":
                        if char == "\"":
                            exp_type = STRING_CONST
                        elif identify_token_from_cats(char, (INT_CONST,)):
                            exp_type = INT_CONST
                            pending_chars += char
                        elif identify_token_from_cats(char, (IDENTIFIER,)):
                            exp_type = IDENTIFIER
                            pending_chars += char
                    elif exp_type == IDENTIFIER and identify_token_from_cats(char, (IDENTIFIER,)):
                        pending_chars += char
                    elif exp_type == INT_CONST and identify_token_from_cats(char, (INT_CONST, )):
                        pending_chars += char
                    else:
                        raise TokenException(f"Invalid token {pending_chars}")

    return None

TokenIterater = iter_each_instruction

