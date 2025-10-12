## Construir um analisador léxico para a liguagem Query SPARQL

### Vitor Costa Pereira, A102515
<img width="180" height="180" alt="pfpuniversidade" src="https://github.com/user-attachments/assets/b350d0f1-1705-4912-b694-09837fb0c79d" />

Para criar o analisador léxico de SPARQL, vamos identificar os tokens da linguagem.<br>
Existem tokens que podem ser identificados por simples expressões regulares como a identificação de um 'select'<br>
que pode ser feito simplesmente por "[Ss][Ee][Ll][Ee][Cc][Tt]".<br>
Porém o SPARQL é uma linguagem Query para RDF. Onde é necessário um atributo tem seu nome e valor definidos da seguinte forma:<br>
nome_atributo:valor_atributo<br>
Portanto para reconhecer os tokens neste caso, temos a expressão regular<br>
"[a-zA-Z_][a-zA-Z0-9_]*:"<br>
para nome do atributo e<br>
"[a-zA-Z_][a-zA-Z0-9_]*"<br>
para valor do atributo. Para que estas expressões regulares reconheçam corretamente estes tokens,<br>
é necessário garantir que são previamente checados a existência de tokens como SELECT ou WHERE.<br>

Tendo estas considerações temos enfim o analisador léxico em python: [(https://github.com/vitorcpereira/PLC2025/TP3/sparql_tokens.py)]