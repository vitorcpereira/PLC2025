import ply.yacc as yacc
import sys
import os
from analexer_pascal import *

def p_Program(t):
    r'Program : PROGRAM ID ";" Code "."'
    # Contar quantas funções existem (cada uma precisa de 1 slot para retorno)
    num_functions = len(parser.functions)
    
    if num_functions > 0:
        return_space = ['pushi 0\n'] * num_functions
        t[0] = return_space + t[4] + ['stop\n']
    else:
        t[0] = t[4] + ['stop\n']

def p_Code(t):
    r'Code : Declarations BEGIN Blocks END'
    global_var_count = parser.varcount
    
    if global_var_count > 0:
        t[0] = ["start\n", f"pushn {global_var_count}\n"] + t[1] + t[3]
    else:
        t[0] = ["start\n"] + t[1] + t[3]

# Declarations
def p_Declarations_vars(t):
    r'Declarations : Vars Declarations'
    t[0] = t[1] + t[2]

def p_Declarations_consts(t):
    r'Declarations : Consts Declarations'
    t[0] = t[1] + t[2]

def p_Declarations_functions(t):
    r'Declarations : Functions Declarations'
    t[0] = t[1] + t[2]

def p_Declarations_procedures(t):
    r'Declarations : Procedures Declarations'
    t[0] = t[1] + t[2]

def p_Declarations_vazio(t):
    r'Declarations : '
    t[0] = []

# CONSTANTES
def p_Consts(t):
    r'Consts : CONST ConstDefs'
    t[0] = []

def p_ConstDefs(t):
    r'ConstDefs : ID "=" ConstValue ";" ConstDefs'
    parser.constants[t[1]] = t[3]
    t[0] = []

def p_ConstDefs_vazio(t):
    r'ConstDefs : '
    t[0] = []

def p_ConstValue_int(t):
    r'ConstValue : INT'
    t[0] = ('int', t[1])

def p_ConstValue_real(t):
    r'ConstValue : REAL'
    t[0] = ('real', t[1])

def p_ConstValue_str(t):
    r'ConstValue : STR'
    t[0] = ('str', t[1])

def p_ConstValue_bool_true(t):
    r'ConstValue : TRUE'
    t[0] = ('bool', True)

def p_ConstValue_bool_false(t):
    r'ConstValue : FALSE'
    t[0] = ('bool', False)

# VARIÁVEIS
def p_Vars(t):
    r'Vars : VAR VarList'
    t[0] = t[2]

def p_VarList(t):
    r'VarList : IDList ":" Type ";" VarList'
    pushcode = []
    
    for var_name in t[1]:
        var_type = t[3]
        if isinstance(var_type, tuple) and var_type[0] == 'array':
            array_size = var_type[2] - var_type[1] + 1
            parser.arrays[var_name] = parser.varcount
            parser.var[var_name] = parser.varcount
            parser.vartype[var_name] = var_type
            parser.scope[var_name] = parser.current_scope
            
            # APENAS para variáveis locais
            if parser.current_scope != 'global':
                pushcode.append(f'pushn {array_size}\n')
            
            parser.varcount += array_size
        else:
            parser.var[var_name] = parser.varcount
            parser.vartype[var_name] = var_type
            parser.scope[var_name] = parser.current_scope
            
            # APENAS para variáveis locais
            if parser.current_scope != 'global':
                pushcode.append(parser.pushdict.get(var_type, 'pushi 0\n'))
            
            parser.varcount += 1
    
    t[0] = t[5] + pushcode

def p_VarList_vazio(t):
    r'VarList : '
    t[0] = []

def p_IDList(t):
    r'IDList : ID RestoIDs'
    t[0] = [t[1]] + t[2]

def p_RestoIDs(t):
    r'RestoIDs : "," ID RestoIDs'
    t[0] = [t[2]] + t[3]

def p_RestoIDs_vazio(t):
    r'RestoIDs : '
    t[0] = []

# TIPOS
def p_Type_integer(t):
    r'Type : INTEGER'
    t[0] = 'integer'

def p_Type_boolean(t):
    r'Type : BOOLEAN'
    t[0] = 'boolean'

def p_Type_string(t):
    r'Type : STRING'
    t[0] = 'string'

def p_Type_real(t):
    r'Type : REALTYPE'
    t[0] = 'real'

def p_Type_char(t):
    r'Type : CHAR'
    t[0] = 'char'

def p_Type_array(t):
    r'Type : ARRAY "[" INT DOTDOT INT "]" OF Type'
    t[0] = ('array', t[3], t[5], t[8])

# FUNÇÕES - GESTÃO DE ESCOPO
def p_Functions(t):
    r'Functions : FUNCTION ID "(" Parameters ")" ":" Type ";" FunctionBody'
    func_name = t[2]
    func_label = f'func{func_name}'
    
    # Guardar contexto global
    old_scope = parser.current_scope
    old_varcount = parser.varcount
    old_var = parser.var.copy()
    old_vartype = parser.vartype.copy()
    old_scope_map = parser.scope.copy()
    
    # Entrar em escopo local
    parser.current_scope = 'local'
    parser.var = {}
    parser.vartype = {}
    parser.scope = {}
    parser.varcount = 0
    parser.num_params = 0
    
    parser.functions[func_name] = func_label
    
    # Processar body
    body_code = t[9]
    num_locals = parser.varcount
    
    # ESTRUTURA: jump end -> label -> pushn locals -> jump body -> body: -> código
    code = [f'jump end{func_label}\n']
    code.append(f'{func_label}:\n')
    
    if num_locals > 0:
        code.append(f'pushn {num_locals}\n')
    
    body_label = f'body{func_label}'
    code.append(f'jump {body_label}\n')
    code.append(f'{body_label}:\n')
    code.extend(body_code)
    code.append('return\n')
    code.append(f'end{func_label}:\n')
    
    # Restaurar contexto global
    parser.current_scope = old_scope
    parser.varcount = old_varcount
    parser.var = old_var
    parser.vartype = old_vartype
    parser.scope = old_scope_map
    
    t[0] = code

def p_Functions_no_params(t):
    r'Functions : FUNCTION ID ":" Type ";" FunctionBody'
    func_name = t[2]
    func_label = f'func{func_name}'
    
    old_scope = parser.current_scope
    old_varcount = parser.varcount
    old_var = parser.var.copy()
    old_vartype = parser.vartype.copy()
    old_scope_map = parser.scope.copy()
    
    parser.current_scope = 'local'
    parser.var = {}
    parser.vartype = {}
    parser.scope = {}
    parser.varcount = 0
    parser.num_params = 0
    parser.functions[func_name] = func_label
    
    code = [f'jump end{func_label}\n']
    code.append(f'{func_label}:\n')
    code.extend(t[6])
    code.append('return\n')
    code.append(f'end{func_label}:\n')
    
    parser.current_scope = old_scope
    parser.varcount = old_varcount
    parser.var = old_var
    parser.vartype = old_vartype
    parser.scope = old_scope_map
    
    t[0] = code

def p_FunctionBody(t):
    r'FunctionBody : Declarations BEGIN Blocks END ";"'
    t[0] = t[1] + t[3]

# PROCEDURES
def p_Procedures(t):
    r'Procedures : PROCEDURE ID "(" Parameters ")" ";" ProcedureBody'
    proc_name = t[2]
    proc_label = f'proc{proc_name}'
    
    old_scope = parser.current_scope
    old_varcount = parser.varcount
    old_var = parser.var.copy()
    old_vartype = parser.vartype.copy()
    old_scope_map = parser.scope.copy()
    
    parser.current_scope = 'local'
    parser.var = {}
    parser.vartype = {}
    parser.scope = {}
    parser.varcount = 0
    parser.functions[proc_name] = proc_label
    
    code = [f'jump end{proc_label}\n']
    code.append(f'{proc_label}:\n')
    code.extend(t[7])
    code.append('return\n')
    code.append(f'end{proc_label}:\n')
    
    parser.current_scope = old_scope
    parser.varcount = old_varcount
    parser.var = old_var
    parser.vartype = old_vartype
    parser.scope = old_scope_map
    
    t[0] = code

def p_Procedures_no_params(t):
    r'Procedures : PROCEDURE ID ";" ProcedureBody'
    proc_name = t[2]
    proc_label = f'proc{proc_name}'
    
    old_scope = parser.current_scope
    old_varcount = parser.varcount
    old_var = parser.var.copy()
    old_vartype = parser.vartype.copy()
    old_scope_map = parser.scope.copy()
    
    parser.current_scope = 'local'
    parser.var = {}
    parser.vartype = {}
    parser.scope = {}
    parser.varcount = 0
    parser.functions[proc_name] = proc_label
    
    code = [f'jump end{proc_label}\n']
    code.append(f'{proc_label}:\n')
    code.extend(t[4])
    code.append('return\n')
    code.append(f'end{proc_label}:\n')
    
    parser.current_scope = old_scope
    parser.varcount = old_varcount
    parser.var = old_var
    parser.vartype = old_vartype
    parser.scope = old_scope_map
    
    t[0] = code

def p_ProcedureBody(t):
    r'ProcedureBody : Declarations BEGIN Blocks END ";"'
    t[0] = t[1] + t[3]

def p_Parameters(t):
    r'Parameters : IDList ":" Type MoreParameters'
    # Parâmetros têm offset NEGATIVO (estão antes do FP)
    for i, param_name in enumerate(t[1]):
        # offset = -(len(t[1]) - i)
        parser.var[param_name] = -(len(t[1]) - i)
        parser.vartype[param_name] = t[3]
        parser.scope[param_name] = 'param'  # NOVO ESCOPO!
        parser.num_params += 1
    t[0] = t[4]

def p_Parameters_vazio(t):
    r'Parameters : '
    t[0] = []

def p_MoreParameters(t):
    r'MoreParameters : ";" IDList ":" Type MoreParameters'
    for param_name in t[2]:
        parser.var[param_name] = -(parser.num_params + 1)
        parser.vartype[param_name] = t[4]
        parser.scope[param_name] = 'param'
        parser.num_params += 1
    t[0] = t[5]

def p_MoreParameters_vazio(t):
    r'MoreParameters : '
    t[0] = []

# BLOCOS
def p_Blocks(t):
    r'Blocks : Block Blocks'
    t[0] = t[1] + t[2]

def p_Blocks_vazio(t):
    r'Blocks : '
    t[0] = []

# I/O - WRITELN
def p_Block_writeln(t):
    r'Block : WRITELN "(" WriteList ")" ";"'
    t[0] = t[3] + ['pushs "\\n"\nwrites\n']

def p_Block_write(t):
    r'Block : WRITE "(" WriteList ")" ";"'
    t[0] = t[3]

def p_WriteList(t):
    r'WriteList : WriteItem MoreWriteItems'
    t[0] = t[1] + t[2]

def p_MoreWriteItems(t):
    r'MoreWriteItems : "," WriteItem MoreWriteItems'
    t[0] = t[2] + t[3]

def p_MoreWriteItems_vazio(t):
    r'MoreWriteItems : '
    t[0] = []

def p_WriteItem_string(t):
    r'WriteItem : STR'
    t[0] = [f'pushs "{t[1]}"\nwrites\n']

def p_WriteItem_exp(t):
    r'WriteItem : Exp'
    t[0] = t[1] + ['writei\n']

def p_Block_readln(t):
    r'Block : READLN "(" ID ")" ";"'
    if t[3] in parser.var:
        var_offset = parser.var[t[3]]
        var_type = parser.vartype.get(t[3], 'integer')
        var_scope = parser.scope.get(t[3], 'global')
        
        store_cmd = 'storel' if var_scope in ['local', 'param'] else 'storeg'
        
        if var_type == 'integer':
            t[0] = [f'read\natoi\n{store_cmd} {var_offset}\n']
        elif var_type == 'string':
            t[0] = [f'read\n{store_cmd} {var_offset}\n']
        else:
            t[0] = [f'read\n{store_cmd} {var_offset}\n']
    else:
        print(f"Erro: variável '{t[3]}' não declarada")
        t[0] = []

def p_Block_readln_array(t):
    r'Block : READLN "(" ID "[" Exp "]" ")" ";"'
    if t[3] in parser.arrays:
        array_base = parser.arrays[t[3]]
        start_index = parser.vartype[t[3]][1]
        var_type = parser.vartype[t[3]][3]
        
        addr_code = [
            "pushgp\n",
            f"pushi {array_base}\n",
            "padd\n"
        ] + t[5] + [
            f"pushi {start_index}\n",
            "sub\n",
            "padd\n"
        ]
        
        if var_type == "integer":
            read_code = ["read\n", "atoi\n"]
        else:
            read_code = ["read\n"]
        
        t[0] = addr_code + read_code + ["store 0\n"]

def p_Block_ass(t):
    r'Block : ID ASSIGN Exp ";"'
    if t[1] in parser.var and t[1] not in parser.arrays:
        var_offset = parser.var[t[1]]
        var_scope = parser.scope.get(t[1], 'global')
        
        # Parâmetros e locais usam STOREL
        if var_scope in ['param', 'local']:
            t[0] = t[3] + [f'storel {var_offset}\n']
        else:  # global
            t[0] = t[3] + [f'storeg {var_offset}\n']
    else:
        t[0] = t[3] + ['storel 0\n']

def p_Block_ass_array(t):
    r'Block : ID "[" Exp "]" ASSIGN Exp ";"'
    if t[1] in parser.arrays:
        array_base = parser.arrays[t[1]]
        start_index = parser.vartype[t[1]][1]
        
        addr_code = [
            "pushgp\n",
            f"pushi {array_base}\n",
            "padd\n"
        ] + t[3] + [
            f"pushi {start_index}\n",
            "sub\n",
            "padd\n"
        ]
        
        t[0] = addr_code + t[6] + ["store 0\n"]

# CONTROLE DE FLUXO - IF
def p_Block_if_then(t):
    r'Block : IF Condition THEN Block'
    label = f'label{parser.labelcount}'
    parser.labelcount += 1
    t[0] = t[2] + [f'jz {label}\n'] + t[4] + [f'{label}:\n']

def p_Block_if_then_else(t):
    r'Block : IF Condition THEN Block ELSE Block'
    label_else = f'label{parser.labelcount}'
    label_end = f'label{parser.labelcount + 1}'
    parser.labelcount += 2
    t[0] = t[2] + [f'jz {label_else}\n'] + t[4] + [f'jump {label_end}\n', f'{label_else}:\n'] + t[6] + [f'{label_end}:\n']

def p_Block_if_then_begin(t):
    r'Block : IF Condition THEN BEGIN Blocks END ";"'
    label = f'label{parser.labelcount}'
    parser.labelcount += 1
    t[0] = t[2] + [f'jz {label}\n'] + t[5] + [f'{label}:\n']

def p_Block_if_then_else_begin(t):
    r'Block : IF Condition THEN BEGIN Blocks END ELSE BEGIN Blocks END ";"'
    label_else = f'label{parser.labelcount}'
    label_end = f'label{parser.labelcount + 1}'
    parser.labelcount += 2
    t[0] = t[2] + [f'jz {label_else}\n'] + t[5] + [f'jump {label_end}\n', f'{label_else}:\n'] + t[9] + [f'{label_end}:\n']

# WHILE
def p_Block_while(t):
    r'Block : WHILE Condition DO Block'
    label_start = f'label{parser.labelcount}'
    label_end = f'label{parser.labelcount + 1}'
    parser.labelcount += 2
    t[0] = [f'{label_start}:\n'] + t[2] + [f'jz {label_end}\n'] + t[4] + [f'jump {label_start}\n', f'{label_end}:\n']

def p_Block_while_begin(t):
    r'Block : WHILE Condition DO BEGIN Blocks END ";"'
    label_start = f'label{parser.labelcount}'
    label_end = f'label{parser.labelcount + 1}'
    parser.labelcount += 2
    t[0] = [f'{label_start}:\n'] + t[2] + [f'jz {label_end}\n'] + t[5] + [f'jump {label_start}\n', f'{label_end}:\n']

def p_Block_for_to(t):
    r'Block : FOR ID ASSIGN Exp TO Exp DO Block'
    if t[2] in parser.var and t[2] not in parser.arrays:
        var_offset = parser.var[t[2]]
        var_scope = parser.scope.get(t[2], 'global')
        
        store_cmd = 'storel' if var_scope in ['local', 'param'] else 'storeg'
        push_cmd = 'pushl' if var_scope in ['local', 'param'] else 'pushg'
        
        label_start = f'label{parser.labelcount}'
        label_end = f'label{parser.labelcount + 1}'
        parser.labelcount += 2
        
        t[0] = t[4] + [f'{store_cmd} {var_offset}\n', 
                      f'{label_start}:\n', 
                      f'{push_cmd} {var_offset}\n'] + t[6] + ['pushi 1\nadd\n'] + [f'inf\njz {label_end}\n'] + t[8] + [
                      f'{push_cmd} {var_offset}\npushi 1\nadd\n{store_cmd} {var_offset}\n',
                      f'jump {label_start}\n',
                      f'{label_end}:\n']
    else:
        t[0] = []

def p_Block_for_to_begin(t):
    r'Block : FOR ID ASSIGN Exp TO Exp DO BEGIN Blocks END ";"'
    if t[2] in parser.var and t[2] not in parser.arrays:
        var_offset = parser.var[t[2]]
        var_scope = parser.scope.get(t[2], 'global')
        
        store_cmd = 'storel' if var_scope in ['local', 'param'] else 'storeg'
        push_cmd = 'pushl' if var_scope in ['local', 'param'] else 'pushg'
        
        label_start = f'label{parser.labelcount}'
        label_end = f'label{parser.labelcount + 1}'
        parser.labelcount += 2
        
        t[0] = t[4] + [f'{store_cmd} {var_offset}\n', 
                      f'{label_start}:\n', 
                      f'{push_cmd} {var_offset}\n'] + t[6] + ['pushi 1\nadd\n'] + [f'inf\njz {label_end}\n'] + t[9] + [
                      f'{push_cmd} {var_offset}\npushi 1\nadd\n{store_cmd} {var_offset}\n',
                      f'jump {label_start}\n',
                      f'{label_end}:\n']
    else:
        t[0] = []

def p_Block_for_downto(t):
    r'Block : FOR ID ASSIGN Exp DOWNTO Exp DO Block'
    if t[2] in parser.var and t[2] not in parser.arrays:
        var_offset = parser.var[t[2]]
        var_scope = parser.scope.get(t[2], 'global')
        
        store_cmd = 'storel' if var_scope in ['local', 'param'] else 'storeg'
        push_cmd = 'pushl' if var_scope in ['local', 'param'] else 'pushg'
        
        label_start = f'label{parser.labelcount}'
        label_end = f'label{parser.labelcount + 1}'
        parser.labelcount += 2
        
        # SEM o "pushi 1 add" inicial!
        t[0] = t[4] + [f'{store_cmd} {var_offset}\n',  # i := início
                      f'{label_start}:\n', 
                      f'{push_cmd} {var_offset}\n'] + t[6] + [  # empilha i e fim
                      'supeq\n',  # i >= fim? (não 'sup'!)
                      f'jz {label_end}\n'] + t[8] + [
                      f'{push_cmd} {var_offset}\n',
                      'pushi 1\n',
                      'sub\n',
                      f'{store_cmd} {var_offset}\n',
                      f'jump {label_start}\n',
                      f'{label_end}:\n']
    else:
        t[0] = []

def p_Block_for_downto_begin(t):
    r'Block : FOR ID ASSIGN Exp DOWNTO Exp DO BEGIN Blocks END ";"'
    if t[2] in parser.var and t[2] not in parser.arrays:
        var_offset = parser.var[t[2]]
        var_scope = parser.scope.get(t[2], 'global')
        
        store_cmd = 'storel' if var_scope in ['local', 'param'] else 'storeg'
        push_cmd = 'pushl' if var_scope in ['local', 'param'] else 'pushg'
        
        label_start = f'label{parser.labelcount}'
        label_end = f'label{parser.labelcount + 1}'
        parser.labelcount += 2
        
        # SEM o "pushi 1 add" inicial!
        t[0] = t[4] + [f'{store_cmd} {var_offset}\n',
                      f'{label_start}:\n', 
                      f'{push_cmd} {var_offset}\n'] + t[6] + [
                      'supeq\n',  # <-- MUDAR DE 'sup' para 'supeq'
                      f'jz {label_end}\n'] + t[9] + [
                      f'{push_cmd} {var_offset}\npushi 1\nsub\n{store_cmd} {var_offset}\n',
                      f'jump {label_start}\n',
                      f'{label_end}:\n']
    else:
        t[0] = []

# REPEAT
def p_Block_repeat(t):
    r'Block : REPEAT Blocks UNTIL Condition ";"'
    label_start = f'label{parser.labelcount}'
    parser.labelcount += 1
    t[0] = [f'{label_start}:\n'] + t[2] + t[4] + [f'jz {label_start}\n']

# CONDIÇÕES
def p_Condition_or(t):
    r'Condition : Condition OR CondTerm'
    t[0] = t[1] + t[3] + ['add\npushi 0\nsup\n']

def p_Condition_term(t):
    r'Condition : CondTerm'
    t[0] = t[1]

def p_CondTerm_and(t):
    r'CondTerm : CondTerm AND CondFactor'
    t[0] = t[1] + t[3] + ['mul\n']

def p_CondTerm_factor(t):
    r'CondTerm : CondFactor'
    t[0] = t[1]

def p_CondFactor_not(t):
    r'CondFactor : NOT CondFactor'
    t[0] = t[2] + ['not\n']

def p_CondFactor_rel(t):
    r'CondFactor : Exp RelOp Exp'
    t[0] = t[1] + t[3] + [t[2]]

def p_CondFactor_paren(t):
    r'CondFactor : "(" Condition ")"'
    t[0] = t[2]

def p_CondFactor_bool_true(t):
    r'CondFactor : TRUE'
    t[0] = ['pushi 1\n']

def p_CondFactor_bool_false(t):
    r'CondFactor : FALSE'
    t[0] = ['pushi 0\n']

def p_CondFactor_id(t):
    r'CondFactor : ID'
    if t[1] in parser.var:
        var_offset = parser.var[t[1]]
        var_scope = parser.scope.get(t[1], 'global')
        
        push_cmd = 'pushl' if var_scope in ['local', 'param'] else 'pushg'
        t[0] = [f'{push_cmd} {var_offset}\n']
    else:
        print(f"Erro: '{t[1]}' não declarado")
        t[0] = []

# OPERADORES RELACIONAIS
def p_RelOp_eq(t):
    r'RelOp : "="'
    t[0] = 'equal\n'

def p_RelOp_ne(t):
    r'RelOp : NE'
    t[0] = 'equal\nnot\n'

def p_RelOp_lt(t):
    r'RelOp : "<"'
    t[0] = 'inf\n'

def p_RelOp_le(t):
    r'RelOp : LE'
    t[0] = 'infeq\n'

def p_RelOp_gt(t):
    r'RelOp : ">"'
    t[0] = 'sup\n'

def p_RelOp_ge(t):
    r'RelOp : GE'
    t[0] = 'supeq\n'

# EXPRESSÕES
def p_Exp_sum(t):
    r'Exp : Exp "+" Term'
    t[0] = t[1] + t[3] + ['add\n']

def p_Exp_sub(t):
    r'Exp : Exp "-" Term'
    t[0] = t[1] + t[3] + ['sub\n']

def p_Exp_term(t):
    r'Exp : Term'
    t[0] = t[1]

def p_Term_mul(t):
    r'Term : Term "*" Factor'
    t[0] = t[1] + t[3] + ['mul\n']

def p_Term_div(t):
    r'Term : Term "/" Factor'
    t[0] = t[1] + t[3] + ['div\n']

def p_Term_div_int(t):
    r'Term : Term DIV Factor'
    t[0] = t[1] + t[3] + ['div\n']

def p_Term_mod(t):
    r'Term : Term MOD Factor'
    t[0] = t[1] + t[3] + ['mod\n']

def p_Term_factor(t):
    r'Term : Factor'
    t[0] = t[1]

# FATORES
def p_Factor_integer(t):
    r'Factor : INT'
    t[0] = [f'pushi {t[1]}\n']

def p_Factor_real(t):
    r'Factor : REAL'
    t[0] = [f'pushf {t[1]}\n']

def p_Factor_string(t):
    r'Factor : STR'
    # Se for um único caractere (como '1'), empilhar como código ASCII
    if len(t[1]) == 1:
        t[0] = [f'pushi {ord(t[1])}\n']  # ord('1') = 49
    else:
        t[0] = [f'pushs "{t[1]}"\n']

def p_Factor_true(t):
    r'Factor : TRUE'
    t[0] = ['pushi 1\n']

def p_Factor_false(t):
    r'Factor : FALSE'
    t[0] = ['pushi 0\n']

def p_Factor_id(t):
    r'Factor : ID'
    if t[1] in parser.constants:
        const_type, const_value = parser.constants[t[1]]
        if const_type == 'int':
            t[0] = [f'pushi {const_value}\n']
        elif const_type == 'real':
            t[0] = [f'pushf {const_value}\n']
        elif const_type == 'str':
            t[0] = [f'pushs "{const_value}"\n']
        elif const_type == 'bool':
            t[0] = [f'pushi {1 if const_value else 0}\n']
    elif t[1] in parser.var and t[1] not in parser.arrays:
        var_offset = parser.var[t[1]]
        var_scope = parser.scope.get(t[1], 'global')
        
        # Parâmetros e locais usam PUSHL
        if var_scope in ['param', 'local']:
            t[0] = [f'pushl {var_offset}\n']
        else:  # global
            t[0] = [f'pushg {var_offset}\n']
    else:
        print(f"Erro: '{t[1]}' não declarado ou é array (use indexação)")
        t[0] = []

def p_Factor_array_access(t):
    r'Factor : ID "[" Exp "]"'
    
    # CASO 1: Acesso a caractere de STRING (bin[i])
    if t[1] in parser.var and parser.vartype.get(t[1]) == 'string':
        var_offset = parser.var[t[1]]
        var_scope = parser.scope.get(t[1], 'global')
        
        push_cmd = 'pushl' if var_scope in ['local', 'param'] else 'pushg'
        
        # Gerar código igual ao exemplo que funciona:
        # PUSHL string, PUSHL index, PUSHI 1, SUB, CHARAT
        t[0] = [
            f'{push_cmd} {var_offset}\n', 
        ] + t[3] + [ 
            'pushi 1\n',
            'sub\n',
            'charat\n'    
        ]
    
    # CASO 2: Acesso a elemento de ARRAY (numeros[i])
    elif t[1] in parser.arrays:
        array_base = parser.arrays[t[1]]
        start_index = parser.vartype[t[1]][1]
        
        t[0] = [
            "pushgp\n",
            f"pushi {array_base}\n",
            "padd\n"
        ] + t[3] + [
            f"pushi {start_index}\n",
            "sub\n",
            "padd\n",
            "load 0\n"
        ]
    
    else:
        print(f"Erro: '{t[1]}' não é array nem string")
        t[0] = []
        
def p_Factor_function_call(t):
    r'Factor : ID "(" ArgumentList ")"'
    if t[1] == 'length':
        t[0] = t[3] + ['strlen\n']
    elif t[1] in parser.functions:
        func_label = parser.functions[t[1]]
        t[0] = t[3] + [f'pusha {func_label}\ncall\n']
    else:
        print(f"Erro: função '{t[1]}' não declarada")
        t[0] = []

def p_Factor_length_call(t):
    r'Factor : LENGTH "(" ArgumentList ")"'
    t[0] = t[3] + ['strlen\n']

def p_Factor_paren(t):
    r'Factor : "(" Exp ")"'
    t[0] = t[2]

def p_ArgumentList(t):
    r'ArgumentList : Exp MoreArguments'
    t[0] = t[1] + t[2]

def p_ArgumentList_vazio(t):
    r'ArgumentList : '
    t[0] = []

def p_MoreArguments(t):
    r'MoreArguments : "," Exp MoreArguments'
    t[0] = t[2] + t[3]

def p_MoreArguments_vazio(t):
    r'MoreArguments : '
    t[0] = []

def p_error(t):
    if t:
        print(f"Erro de sintaxe em '{t.value}' na linha {t.lineno}")
    else:
        print("Erro de sintaxe: fim de arquivo inesperado")

lexer.lineno = 1
parser = yacc.yacc()

# Função para resetar o estado do parser
def reset_parser():
    parser.var = {}
    parser.arrays = {}
    parser.array_bounds = {}
    parser.vartype = {}
    parser.constants = {}
    parser.functions = {}
    parser.scope = {}
    parser.current_scope = 'global'
    parser.varcount = 0
    parser.labelcount = 0
    parser.num_params = 0

    parser.pushdict = {
        'integer': 'pushi 0\n',
        'real': 'pushf 0.0\n',
        'string': 'pushs ""\n',
        'boolean': 'pushi 0\n',
        'char': 'pushi 0\n'
    }

# Reset inicial
reset_parser()

if __name__ == "__main__":
    # Verificar se foi passado um arquivo como argumento
    if len(sys.argv) < 2:
        print("Uso: python compilador.py <arquivo.pas>")
        print("Exemplo: python compilador.py programa.pas")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    # Verificar se o arquivo existe
    if not os.path.exists(input_file):
        print(f"Erro: Arquivo '{input_file}' nao encontrado.")
        sys.exit(1)
    
    # Gerar nome do arquivo de saida
    base_name = os.path.splitext(input_file)[0]
    output_file = base_name + '.ewvm'
    
    # Ler o codigo Pascal do arquivo
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            codigo_pascal = f.read()
        print(f"Lendo arquivo: {input_file}")
    except Exception as e:
        print(f"Erro ao ler arquivo {input_file}: {e}")
        sys.exit(1)
    
    # Resetar o parser para novo arquivo
    reset_parser()
    
    # Compilar o codigo
    try:
        print(f"Compilando {input_file}...")
        result = parser.parse(codigo_pascal)
        
        if result:
            # Converter resultado para string
            codigo_gerado = "".join(result)
            
            # IMPRIMIR o codigo gerado
            print("\n" + "="*50)
            print("CODIGO GERADO (.ewvm):")
            print("="*50)
            print(codigo_gerado)
            print("="*50 + "\n")
            
            # Escrever o resultado no arquivo .ewvm
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(codigo_gerado)
                print("Compilacao concluida com sucesso!")
                print(f"Arquivo gerado: {output_file}")
                print(f"Tamanho: {len(codigo_gerado.splitlines())} linhas de codigo")
            except Exception as e:
                print(f"Erro ao escrever arquivo {output_file}: {e}")
                sys.exit(1)
        else:
            print(f"Erro: Nao foi possivel gerar codigo para {input_file}")
            sys.exit(1)
            
    except Exception as e:
        print(f"Erro durante a compilacao: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
