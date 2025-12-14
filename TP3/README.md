## Conversor de MarkDown para HTML

### Vitor Costa Pereira, A102515
<img width="180" height="180" alt="pfpuniversidade" src="https://github.com/user-attachments/assets/b350d0f1-1705-4912-b694-09837fb0c79d" />

Para criar o conversor de MarkDown para HTML, vamos criar funções que convertem cada elemento específico descrito na "Basic Syntax".<br>
Em cada uma dessas funções vamos utilizar a função sub do módulo re.<br>
Na definição da função listanumerada, por exemplo, utilizamos a expressão regular r'\d+\.\s(.+)\b' que identifica um numero seguido de um ponto ".", seguido de um espaco, capturamos o texto com (.+) e identificamos o fim da linha ou ficheiro com \b.<br>
Apos a definicao de todas funções, criamos a função markdown_to_html que utiliza todas essas funções para fazer o conversor para os elementos descritos na "Basic Syntax". Isto é feito tendo em atenção por exemplo que a função bold deve vir antes da função italico, uma vez que ambas identificam texto entres astericos "*", a funcao bold entre 2 asteriscos e a funcao italico entre 1 asterisco. Portanto a funcao bold deve ser corrida anterior a funcao italico para evitar que os asteriscos que sejam utilizados para bold sejam identificados como italico.<br>
<br>
O conversor final:
[(https://github.com/vitorcpereira/PLC2025/blob/master/TP3/convertemd.py)]
