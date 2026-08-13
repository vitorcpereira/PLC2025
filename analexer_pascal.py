import ply.lex as lex

# Lista de nomes de tokens
tokens = (
    # palavras reservadas
    'AND', 'ARRAY', 'BEGIN', 'CASE', 'CONST', 'DIV', 'DO', 'DOWNTO', 'ELSE', 'END',
    'FILE', 'FOR', 'FUNCTION', 'GOTO', 'IF', 'IN', 'LABEL', 'MOD', 'NIL', 'NOT',
    'OF', 'OR', 'PACKED', 'PROCEDURE', 'PROGRAM', 'RECORD', 'REPEAT', 'SET', 'STRING', 'THEN',
    'TO', 'TYPE', 'UNTIL', 'VAR', 'WHILE', 'WITH', 'FORWARD', 'INTEGER', 'WRITELN', 'READLN',
    'LENGTH', 'TRUE', 'FALSE', 'CHAR', 'REALTYPE', 'WRITE', 'READ',
    # simbolos
    'NE', 'LE', 'GE', 'ASSIGN', 'DOTDOT',
    # tipos de dados
    'ID', 'INT', 'BOOLEAN', 'REAL', 'STR', 'COMMENT'
)

literals = ('+', '-', '*', '/', '=', '<', '>', '[', ']', '.', ',', ':', ';', '^', '(', ')')

reserved = {
    'and': 'AND',
    'array': 'ARRAY',
    'begin': 'BEGIN',
    'boolean': 'BOOLEAN',
    'case': 'CASE',
    'char': 'CHAR',
    'const': 'CONST',
    'div': 'DIV',
    'do': 'DO',
    'downto': 'DOWNTO',
    'else': 'ELSE',
    'end': 'END',
    'file': 'FILE',
    'for': 'FOR',
    'function': 'FUNCTION',
    'goto': 'GOTO',
    'if': 'IF',
    'integer': 'INTEGER',
    'in': 'IN',
    'label': 'LABEL',
    'mod': 'MOD',
    'nil': 'NIL',
    'not': 'NOT',
    'of': 'OF',
    'or': 'OR',
    'packed': 'PACKED',
    'procedure': 'PROCEDURE',
    'program': 'PROGRAM',
    'read': 'READ',
    'readln': 'READLN',
    'real': 'REALTYPE',
    'record': 'RECORD',
    'repeat': 'REPEAT',
    'set': 'SET',
    'string': 'STRING',
    'then': 'THEN',
    'to': 'TO',
    'type': 'TYPE',
    'until': 'UNTIL',
    'var': 'VAR',
    'while': 'WHILE',
    'with': 'WITH',
    'write': 'WRITE',
    'writeln': 'WRITELN',
    'forward': 'FORWARD',
    'length': 'LENGTH',
    'true': 'TRUE',
    'false': 'FALSE',
}

def t_COMMENT(t):
    r'\(\*[^*]*\*+(?:[^*)*][^*]*\*+)*\)|\{[^}]*\}'
    t.lexer.lineno += t.value.count('\n')
    pass

def t_STR(t):
    r"'(?:''|[^'])*'"
    t.value = t.value[1:-1].replace("''", "'")
    return t

def t_REAL(t):
    r'\d+\.\d+([eE][+-]?\d+)?|\.\d+([eE][+-]?\d+)?|\d+[eE][+-]?\d+'
    t.value = float(t.value)
    return t

def t_INT(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_NE(t):
    r'<>'
    return t

def t_LE(t):
    r'<='
    return t

def t_GE(t):
    r'>='
    return t

def t_ASSIGN(t):
    r':='
    return t

def t_DOTDOT(t):
    r'\.\.'
    return t

def t_ID(t):
    r'[a-zA-Z][a-zA-Z0-9]*'
    t.type = reserved.get(t.value.lower(), 'ID') 
    return t

t_ignore = ' \t'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Caractere ilegal '{t.value[0]}' na linha {t.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()