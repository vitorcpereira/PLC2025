## Expressão regular que represente strings binárias que não contém a substring 011

### Vitor Costa Pereira, A102515
<img width="180" height="180" alt="pfpuniversidade" src="https://github.com/user-attachments/assets/b350d0f1-1705-4912-b694-09837fb0c79d" />


Para criar uma expressão regular que represente strings binárias que não contém a substring 011, 
podemos começar por considerar, por exemplo a string binária que tem um número indeterminado de caracteres 1


1\*


Após isso, consideramos a possibilidade da existência indeterminada de caracteres 0

1\*0\*

De seguida, limitamos a aparição de caracteres 1 após um número indeterminado de caracteres 0, que é 0 ou 1, podendo se representar por ?

1\*(0\*1?)

E consideramos, por fim, que uma sequencia indeterminada de caracteres 0 seguida por, ou interrompida por 0 ou 1 caracteres 1, pode acontecer um número indeterminado de vezes

1\*(0\*1?)\*

A expressão regular resultante pode ser testada através do seguinte link
[(https://regex101.com/r/H0EHjR/2)]
