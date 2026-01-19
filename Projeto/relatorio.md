# Processamento de Linguagens e Compiladores

## Construção de um compilador em Pascal
### Grupo 13
* Vitor Pereira - A102515
* Hugo Gomes - A100056
* Gustavo Gomes - A101777

## Introdução

Este trabalho consiste no desenvolvimento de um compilador para a linguagem Pascal Standard, no âmbito da disciplina de Processamento de Linguagens e Compiladores. O objetivo é criar um compilador funcional capaz de processar código Pascal e convertê-lo para código executável numa máquina virtual. 

O desenvolvimento do compilador segue as seguintes etapas: análise léxica, análise sintática, análise semântica e geração de código. O compilador final processa código Pascal e gera código executável para uma máquina virtual. 

Este relatório apresenta a implementação realizada e os testes efetuados. 

## 1. Análise Léxica
O analisador léxico (lexer) é então a primeira etapa do processo de compilação. 

O lexer desenvolvido neste projeto foi implementado em Python, recorrendo à biblioteca PLY (Python Lex-Yacc). 

O objetivo deste componente é converter o texto bruto do programa numa sequência de símbolos terminais (tokens) compreensíveis pelo parser. São identificados elementos como palavras reservadas, identificadores, operadores, literais e símbolos especiais, enquanto são descartados comentários e espaços em branco. 
## 1.1. Tokens
Começamos por definir todos os tokens relevantes, incluindo palavras reservadas, identificadores, literais numéricos (inteiros e reais), valores booleanos, strings, caracteres, operadores relacionais, símbolos especiais (como atribuição e intervalos) e comentários. 

```python
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
```

As palavras reservadas são identificadas através de uma consulta a um dicionário específico, onde o texto capturado é convertido para minúsculas, garantindo assim a insensibilidade a maiúsculas/minúsculas (case-insensitivity) típica do Pascal. 

```python
def t_ID(t):
    r'[a-zA-Z][a-zA-Z0-9]*'
    t.type = reserved.get(t.value.lower(), 'ID') 
    return t
```

Os identificadores são reconhecidos por uma expressão regular que aceita uma letra inicial seguida de letras ou dígitos (alfanuméricos), sendo posteriormente verificados contra a lista de palavras reservadas. 

Os números são divididos em duas categorias: inteiros, formados por sequências de dígitos, e reais, que suportam ponto decimal e notação científica. 

```python
def t_REAL(t):
    r'\d+\.\d+([eE][+-]?\d+)?|\.\d+([eE][+-]?\d+)?|\d+[eE][+-]?\d+'
    t.value = float(t.value)
    return t
```

O reconhecimento de strings utiliza exclusivamente aspas simples (plicas), conforme o padrão Pascal, incluindo o tratamento de aspas escapadas no interior da cadeia. 

```python
def t_STR(t):
    r"'(?:''|[^'])*'"
    t.value = t.value[1:-1].replace("''", "'")
    return t
```

Definimos tokens específicos para operadores compostos (como :=, <=, <>, ..), enquanto os operadores de um só caractere (como +, -, ;) são tratados como literais diretos. 

Os comentários são ignorados pelo lexer e podem ser escritos em dois dos formatos aceites em Pascal: blocos entre chavetas { ... } e blocos entre (* ... *). 

Espaços e tabulações são ignorados, sendo as quebras de linha processadas apenas para incrementar o contador de linhas.  

```python
def t_COMMENT(t):
    r'\(\*[^*]*\*+(?:[^*)*][^*]*\*+)*\)|\{[^}]*\}'
    t.lexer.lineno += t.value.count('\n')
    pass

t_ignore = ' \t'
```

Sempre que um carácter ilegal é detetado, o analisador emite uma mensagem de erro indicando a linha da ocorrência." 

```python
def t_error(t):
    print(f"Caractere ilegal '{t.value[0]}' na linha {t.lineno}")
    t.lexer.skip(1)
```


## 2. Análise sintática
Após a análise léxica, o passo seguinte no processo de compilação é a análise sintática. 

Nesta fase, recorreu-se à biblioteca PLY (Python Lex-Yacc) para a implementação. Foram elaboradas regras sintáticas para permitir o reconhecimento das construções fundamentais da linguagem Pascal, tais como a declaração de variáveis, estruturas de controlo e operações aritméticas. 

O objetivo principal desta etapa consiste em validar se a sequência de tokens gerada anteriormente respeita as normas gramaticais da linguagem. Caso o código seja válido, o analisador organiza a informação numa estrutura lógica que permite o processamento posterior pelo compilador. 

## 2.1. Gramática
A gramática do nosso compilador Pascal foi desenvolvida para ser compatível com o parser LALR(1) da biblioteca PLY (Python Lex-Yacc). Trata-se de uma gramática independente de contexto, recursiva à esquerda, que suporta as principais construções da linguagem Pascal Standard, incluindo funcionalidades avançadas como arrays, funções, procedimentos e constantes. 

A precedência e associatividade dos operadores são definidas implicitamente através da estrutura hierárquica da gramática, garantindo que as operações aritméticas e lógicas são avaliadas na ordem correta. 

### Estrutura do programa
A regra p_Program define a estrutura global de um programa Pascal, que deve começar com a palavra-chave program, seguida de um identificador, declarações opcionais e o bloco principal delimitado por begin e end. 

```python
def p_Program(t):
    r'Program : PROGRAM ID ";" Code "."'
    t[0] = t[4] + ['stop\n']
```
A regra p_Code organiza o programa em declarações (variáveis, constantes, funções e procedimentos) seguidas do bloco de comandos principal. O código gerado insere a instrução start no início, seguida pelas alocações de variáveis globais. 

```python
def p_Code(t):
    r'Code : Declarations BEGIN Blocks END'
    # O start deve vir ANTES das variáveis globais e do código
    t[0] = ["start\n"] + t[1] + t[3]
```

### Declarações
O compilador suporta quatro tipos de declarações, processadas pela regra p_Declarations: 

* Variáveis (VAR)
* Constantes (CONST)
* Funções (FUNCTION)
* Procedimentos (PROCEDURE)

```python
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
```

### Variáveis
As variáveis são declaradas através de listas de identificadores associados a tipos. A regra p_VarList processa cada declaração e regista as variáveis na tabela de símbolos (parser.var), associando-as a offsets na stack global.

```python
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
            pushcode.append(f'pushn {array_size}\n')
            parser.varcount += array_size
        else:
            parser.var[var_name] = parser.varcount
            parser.vartype[var_name] = var_type
            pushcode.append(parser.pushdict.get(var_type, 'pushi 0\n'))
            parser.varcount += 1
    
    t[0] = t[5] + pushcode
```
Detalhe importante: O código de alocação é inserido na ordem inversa (t[5] + pushcode) para garantir que os índices na stack correspondam à ordem de declaração no código fonte. 

### Arrays

Arrays são suportados através da sintaxe array[inicio..fim] de tipo. A implementação utiliza a instrução pushn para alocar espaço contíguo e regista o offset base e os limites em estruturas auxiliares: 
```python
def p_Type_array(t):
    r'Type : ARRAY "[" INT DOTDOT INT "]" OF Type'
    t[0] = ('array', t[3], t[5], t[8])
```

O acesso a elementos do array é feito através de cálculo dinâmico de endereços: 
```python
def p_Factor_array_access(t):
    r'Factor : ID "[" Exp "]"'
    if t[1] in parser.arrays:
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
        t[0] = []
```

### Consatntes
As constantes são processadas em tempo de compilação e armazenadas num dicionário (parser.constants). Quando referenciadas no código, são substituídas diretamente pelos seus valores: 

```python
def p_ConstDefs(t):
    r'ConstDefs : ID "=" ConstValue ";" ConstDefs'
    parser.constants[t[1]] = t[3]
    t[0] = []
```

### Funções e procedimentos
Funções e procedimentos são compilados como blocos de código com labels únicos, precedidos por um salto incondicional que evita a sua execução durante o fluxo normal do programa: 
```python
def p_Functions(t):
    r'Functions : FUNCTION ID "(" Parameters ")" ":" Type ";" FunctionBody'
    func_name = t[2]
    func_label = f'func{func_name}'
    
    parser.functions[func_name] = func_label
    
    code = [f'jump end{func_label}\n']
    code.append(f'{func_label}:\n')
    code.extend(t[9])
    code.append('return\n')
    code.append(f'end{func_label}:\n')
    
    t[0] = code
```
Os parâmetros são registados como variáveis locais na tabela de símbolos durante a análise da lista de parâmetros. 

### Blocos de código

Os comandos suportados incluem atribuições, estruturas de controlo (if, while, for, repeat), entrada/saída (read, write) e chamadas a funções/procedimentos. 

**Atribuições** 

As atribuições calculam a expressão do lado direito e armazenam o resultado na variável indicada: 

```python
def p_Block_ass(t):
    r'Block : ID ASSIGN Exp ";"'
    if t[1] in parser.var and t[1] not in parser.arrays:
        var_offset = parser.var[t[1]]
        t[0] = t[3] + [f'storeg {var_offset}\n']
    else:
        t[0] = t[3] + ['storel 0\n']
```
Para arrays, o código calcula o endereço do elemento antes de armazenar: 
```python
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
```

**Estrutura Condicional (If) **

O if gera labels para controlar o fluxo de execução. A condição é avaliada e, se falsa (jz), salta para o bloco else ou para o fim: 

```python
def p_Block_if_then_else(t):
    r'Block : IF Condition THEN Block ELSE Block'
    label_else = f'label{parser.labelcount}'
    label_end = f'label{parser.labelcount + 1}'
    parser.labelcount += 2
    t[0] = t[2] + [f'jz {label_else}\n'] + t[4] + [f'jump {label_end}\n', f'{label_else}:\n'] + t[6] + [f'{label_end}:\n']
```

**Ciclo While **

O while utiliza dois labels: um para o início do ciclo e outro para a saída. A condição é verificada em cada iteração: 
```python
def p_Block_while(t):
    r'Block : WHILE Condition DO Block'
    label_start = f'label{parser.labelcount}'
    label_end = f'label{parser.labelcount + 1}'
    parser.labelcount += 2
    t[0] = [f'{label_start}:\n'] + t[2] + [f'jz {label_end}\n'] + t[4] + [f'jump {label_start}\n', f'{label_end}:\n']
```

**Ciclo For **

O for é implementado com inicialização da variável de controlo, verificação de limite e incremento automático. Suporta tanto to (crescente) como downto (decrescente): 
```python
def p_Block_for_to(t):
    r'Block : FOR ID ASSIGN Exp TO Exp DO Block'
    if t[2] in parser.var and t[2] not in parser.arrays:
        var_offset = parser.var[t[2]]
        label_start = f'label{parser.labelcount}'
        label_end = f'label{parser.labelcount + 1}'
        parser.labelcount += 2
        
        t[0] = t[4] + [f'storeg {var_offset}\n', 
                      f'{label_start}:\n', 
                      f'pushg {var_offset}\n'] + t[6] + ['pushi 1\nadd\n'] + [f'inf\njz {label_end}\n'] + t[8] + [
                      f'pushg {var_offset}\npushi 1\nadd\nstoreg {var_offset}\n',
                      f'jump {label_start}\n',
                      f'{label_end}:\n']
    else:
        t[0] = []
```

**Ciclo Repeat-Until **

O repeat executa o bloco pelo menos uma vez, verificando a condição no final: 
```python
def p_Block_repeat(t):
    r'Block : REPEAT Blocks UNTIL Condition ";"'
    label_start = f'label{parser.labelcount}'
    parser.labelcount += 1
    t[0] = [f'{label_start}:\n'] + t[2] + t[4] + [f'jz {label_start}\n']
```

**Entrada e Saída **

**Leitura** (readln): Lê um valor da entrada padrão e converte-o conforme o tipo da variável: 
```python
def p_Block_readln(t):
    r'Block : READLN "(" ID ")" ";"'
    if t[3] in parser.var:
        var_offset = parser.var[t[3]]
        var_type = parser.vartype.get(t[3], 'integer')
        
        if var_type == 'integer':
            t[0] = [f'read\natoi\nstoreg {var_offset}\n']
        elif var_type == 'string':
            t[0] = [f'read\nstoreg {var_offset}\n']
        else:
            t[0] = [f'read\nstoreg {var_offset}\n']
    else:
        print(f"Erro: variável '{t[3]}' não declarada")
        t[0] = []
```

**Escrita** (write/writeln): Imprime uma lista de valores, que podem ser strings literais ou expressões: 
```python
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
```

### Expressões e Condições 

As expressões aritméticas seguem a hierarquia tradicional: Exp (soma/subtração) → Term (multiplicação/divisão/módulo) → Factor (valores atómicos). 

```python
def p_Exp_sum(t):
    r'Exp : Exp "+" Term'
    t[0] = t[1] + t[3] + ['add\n']

def p_Term_mul(t):
    r'Term : Term "*" Factor'
    t[0] = t[1] + t[3] + ['mul\n']
```

As condições lógicas seguem uma estrutura similar: Condition (OR) → CondTerm (AND) → CondFactor (NOT, comparações): 
```python
def p_Condition_or(t):
    r'Condition : Condition OR CondTerm'
    t[0] = t[1] + t[3] + ['or\n']

def p_CondFactor_not(t):
    r'CondFactor : NOT CondFactor'
    t[0] = t[2] + ['not\n']

def p_CondFactor_rel(t):
    r'CondFactor : Exp RelOp Exp'
    t[0] = t[1] + t[3] + [t[2]]
```
Operadores relacionais suportados: =, <>, <, <=, >, >=. 

## 2.2. Gestão de Escopos e Subprogramas

Para permitir a utilização de funções e procedimentos, o compilador implementa uma gestão de escopos que distingue entre variáveis **globais** e **locais**. Esta distinção é fundamental para garantir a integridade dos dados e permitir a recursividade.

### Memória Global e Local
A gestão de memória na máquina virtual é feita através de dois registadores principais: o *Global Pointer* (GP) e o *Frame Pointer* (FP). 
*As variáveis declaradas no bloco principal do programa são consideradas **globais** e acedidas através das instruções `pushg` e `storeg`.
*As variáveis declaradas dentro de funções, bem como os seus parâmetros, são **locais**. Estas são geridas no *stack frame* da função e acedidas com as instruções `pushl` e `storel`, que utilizam endereços relativos ao `FP`.



### Implementação do Contexto
No código Python (`anasinfinal.py`), esta lógica é controlada pelo atributo `parser.current_scope`. 
1. Quando o parser entra numa função, o escopo muda para o nome da função e o contador de variáveis locais é reiniciado.
2. Os parâmetros são inseridos na tabela de símbolos como as primeiras posições do novo contexto (`FP+0`, `FP+1`, etc.).
3. Ao gerar código para um identificador, o compilador verifica primeiro se este existe no escopo local; se não encontrar, procura no escopo global.

**Exemplo de diferenciação no código:**

```pascal
program ExemploEscopo;
var g: integer; { Global }

function dobro(n: integer): integer;
var local: integer; { Local }
begin
    local := n * 2;
    dobro := local;
end;

begin
    readln(g);
    writeln(dobro(g));
end.
```



## 3. Testes

## 3.1. Olá, Mundo!
### Input
```pascal
program HelloWorld;
begin
writeln('Ola, Mundo!');
end.
```
### Output
```
start
pushs "Ola, Mundo!"
writes
pushs "\n"
writes
stop
```

## 3.2. Fatorial
### Input
```pascal
program Fatorial;
var
n, i, fat: integer;
begin
writeln('Introduza um número inteiro positivo:');
readln(n);
fat := 1;
for i := 1 to n do
fat := fat * i;
writeln('Fatorial de ', n, ': ', fat);
end.
```
### Output
```
start
pushn 3
pushs "Introduza um número inteiro positivo:"
writes
pushs "\n"
writes
read
atoi
storeg 0
pushi 1
storeg 2
pushi 1
storeg 1
label0:
pushg 1
pushg 0
pushi 1
add
inf
jz label1
pushg 2
pushg 1
mul
storeg 2
pushg 1
pushi 1
add
storeg 1
jump label0
label1:
pushs "Fatorial de "
writes
pushg 0
writei
pushs ": "
writes
pushg 2
writei
pushs "\n"
writes
stop

```


## 3.3. Verificação de Número Primo
### Input
```pascal
program NumeroPrimo;
var
num, i: integer;
primo: boolean;
begin
writeln('Introduza um número inteiro positivo:');
readln(num);
primo := true;
i := 2;
while (i <= (num div 2)) and primo do
begin
if (num mod i) = 0 then
primo := false;
i := i + 1;
end;
if primo then
writeln(num, ' é um número primo')
else
writeln(num, ' não é um número primo')
end.
```
### Output
```
start
pushn 3
pushs "Introduza um número inteiro positivo:"
writes
pushs "\n"
writes
read
atoi
storeg 1
pushi 1
storeg 0
pushi 2
storeg 2
label1:
pushg 2
pushg 1
pushi 2
div
infeq
pushg 0
mul
jz label2
pushg 1
pushg 2
mod
pushi 0
equal
jz label0
pushi 0
storeg 0
label0:
pushg 2
pushi 1
add
storeg 2
jump label1
label2:
pushg 0
jz label3
pushg 1
writei
pushs " é um número primo"
writes
pushs "\n"
writes
jump label4
label3:
pushg 1
writei
pushs " não é um número primo"
writes
pushs "\n"
writes
label4:
stop

```


## 3.4. Soma de uma lista de inteiros
### Input
```pascal
program SomaArray;
var
numeros: array[1..5] of integer;
i, soma: integer;
begin
soma := 0;
writeln('Introduza 5 números inteiros:');
for i := 1 to 5 do
begin
readln(numeros[i]);
soma := soma + numeros[i];
end;
writeln('A soma dos números é: ', soma);
end.
```
### Output
```
start
pushn 7
pushi 0
storeg 1
pushs "Introduza 5 números inteiros:"
writes
pushs "\n"
writes
pushi 1
storeg 0
label0:
pushg 0
pushi 5
pushi 1
add
inf
jz label1
pushgp
pushi 2
padd
pushg 0
pushi 1
sub
padd
read
atoi
store 0
pushg 1
pushgp
pushi 2
padd
pushg 0
pushi 1
sub
padd
load 0
add
storeg 1
pushg 0
pushi 1
add
storeg 0
jump label0
label1:
pushs "A soma dos números é: "
writes
pushg 1
writei
pushs "\n"
writes
stop
```


## 3.5. Conversão binário-decimal
### Input
```pascal
program BinarioParaInteiro;
function BinToInt(bin: string): integer;
var
i, valor, potencia: integer;
begin
valor := 0;
potencia := 1;
for i := length(bin) downto 1 do
begin
if bin[i] = '1' then
valor := valor + potencia;
potencia := potencia * 2;
end;
BinToInt := valor;
end;
var
bin: string;
valor: integer;
begin
writeln('Introduza uma string binária:');
readln(bin);
valor := BinToInt(bin);
writeln('O valor inteiro correspondente é: ', valor);
end.
```
### Output
```
pushi 0
start
pushn 5
jump endfuncBinToInt
funcBinToInt:
jump bodyfuncBinToInt
bodyfuncBinToInt:
pushi 0
storeg 1
pushi 1
storeg 2
pushl -1
strlen
storeg 0
label1:
pushg 0
pushi 1
supeq
jz label2
pushl -1
pushg 0
pushi 1
sub
charat
pushi 49
equal
jz label0
pushg 1
pushg 2
add
storeg 1
label0:
pushg 2
pushi 2
mul
storeg 2
pushg 0
pushi 1
sub
storeg 0
jump label1
label2:
pushg 1
storel 0
return
endfuncBinToInt:
pushs "Introduza uma string binária:"
writes
pushs "\n"
writes
read
storeg 4
pushg 4
pusha funcBinToInt
call
storeg 3
pushs "O valor inteiro correspondente é: "
writes
pushg 3
writei
pushs "\n"
writes
stop
```


## Conclusão

Este trabalho permitiu-nos desenvolver um compilador funcional para a linguagem Pascal, consolidando na prática os conceitos aprendidos em Processamento de Linguagens. Apesar de alguns desafios encontrados na implementação completa da análise semântica, o compilador cumpre os objetivos principais, traduzindo algoritmos complexos para a máquina virtual EWVM com desempenho satisfatório.

Embora certas funcionalidades da linguagem tenham sido abordadas de forma mais superficial por opção de projeto, o resultado final é coerente e bem fundamentado. A experiência permitiu-nos dominar ferramentas como ply.lex e ply.yacc, compreendendo melhor as fases de construção de um compilador. No geral, o grupo está satisfeito com o conhecimento adquirido e com a ferramenta funcional que desenvolvemos, que demonstra a complexidade e o fascínio da tradução de linguagens de programação.
