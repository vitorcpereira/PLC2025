
import sys
import re

def tokenize(input_string):
    reconhecidos = []
    mo = re.finditer(r'(?P<COMENTARIO>#.*\n)|(?P<SEL>[Ss][Ee][Ll][Ee][Cc][Tt])|(?P<WHR>[Ww][Hh][Ee][Rr][Ee])|(?P<LIM>[Ll][Ii][Mm][Ii][Tt])|(?P<A_KEYWORD>\ba\b)|(?P<DSTNCT>[Dd][Ii][Ss][Tt][Ii][Nn][Cc][Tt])|(?P<OPTNL>[Oo][Pp][Tt][Ii][Oo][Nn][Aa][Ll])|(?P<FLTR>[Ff][Ii][Ll][Tt][Ee][Rr])|(?P<ORDER>[Oo][Rr][Dd][Ee][Rr])|(?P<BY>[Bb][Yy])|(?P<ASC>[Aa][Ss][Cc])|(?P<DESC>[Dd][Ee][Ss][Cc])|(?P<NOME_ATRIBUTO>[a-zA-Z_][a-zA-Z0-9_]*:)|(?P<VALOR_ATRIBUTO>[a-zA-Z_][a-zA-Z0-9_]*)|(?P<VAR>\?[a-zA-Z_][a-zA-Z0-9_]*)|(?P<IRI><[^>]*>)|(?P<STRING>"[^"]*"(@[a-z]+(-[a-z0-9]+)*)?)|(?P<NUM>\d+(\.\d+)?)|(?P<AC>\{)|(?P<FC>\})|(?P<AP>\()|(?P<FP>\))|(?P<PONTO>\.)|(?P<VRGL>,)|(?P<PNTVRGL>;)|(?P<IGUAL>=)|(?P<DIFERENTE>!=)|(?P<MENOS><)|(?P<MAIS>>)|(?P<AND>&&)|(?P<OR>\|\|)|(?P<NOT>!)|(?P<SKIP>[ \t]+)|(?P<NEWLINE>\n)|(?P<ERRO>.)', input_string)
    for m in mo:
        dic = m.groupdict()
        if dic['COMENTARIO']:
            t = ("COMENTARIO", dic['COMENTARIO'], nlinha, m.span())

        elif dic['SEL']:
            t = ("SEL", dic['SEL'], nlinha, m.span())
    
        elif dic['WHR']:
            t = ("WHR", dic['WHR'], nlinha, m.span())
    
        elif dic['LIM']:
            t = ("LIM", dic['LIM'], nlinha, m.span())
    
        elif dic['A_KEYWORD']:
            t = ("A_KEYWORD", dic['A_KEYWORD'], nlinha, m.span())
    
        elif dic['DSTNCT']:
            t = ("DSTNCT", dic['DSTNCT'], nlinha, m.span())
    
        elif dic['OPTNL']:
            t = ("OPTNL", dic['OPTNL'], nlinha, m.span())
    
        elif dic['FLTR']:
            t = ("FLTR", dic['FLTR'], nlinha, m.span())
    
        elif dic['ORDER']:
            t = ("ORDER", dic['ORDER'], nlinha, m.span())
    
        elif dic['BY']:
            t = ("BY", dic['BY'], nlinha, m.span())
    
        elif dic['ASC']:
            t = ("ASC", dic['ASC'], nlinha, m.span())
    
        elif dic['DESC']:
            t = ("DESC", dic['DESC'], nlinha, m.span())
    
        elif dic['NOME_ATRIBUTO']:
            t = ("NOME_ATRIBUTO", dic['NOME_ATRIBUTO'], nlinha, m.span())
    
        elif dic['VALOR_ATRIBUTO']:
            t = ("VALOR_ATRIBUTO", dic['VALOR_ATRIBUTO'], nlinha, m.span())
    
        elif dic['VAR']:
            t = ("VAR", dic['VAR'], nlinha, m.span())
    
        elif dic['IRI']:
            t = ("IRI", dic['IRI'], nlinha, m.span())
    
        elif dic['STRING']:
            t = ("STRING", dic['STRING'], nlinha, m.span())
    
        elif dic['NUM']:
            t = ("NUM", dic['NUM'], nlinha, m.span())
    
        elif dic['AC']:
            t = ("AC", dic['AC'], nlinha, m.span())
    
        elif dic['FC']:
            t = ("FC", dic['FC'], nlinha, m.span())
    
        elif dic['AP']:
            t = ("AP", dic['AP'], nlinha, m.span())
    
        elif dic['FP']:
            t = ("FP", dic['FP'], nlinha, m.span())
    
        elif dic['PONTO']:
            t = ("PONTO", dic['PONTO'], nlinha, m.span())
    
        elif dic['VRGL']:
            t = ("VRGL", dic['VRGL'], nlinha, m.span())
    
        elif dic['PNTVRGL']:
            t = ("PNTVRGL", dic['PNTVRGL'], nlinha, m.span())
    
        elif dic['IGUAL']:
            t = ("IGUAL", dic['IGUAL'], nlinha, m.span())
    
        elif dic['DIFERENTE']:
            t = ("DIFERENTE", dic['DIFERENTE'], nlinha, m.span())
    
        elif dic['MENOS']:
            t = ("MENOS", dic['MENOS'], nlinha, m.span())
    
        elif dic['MAIS']:
            t = ("MAIS", dic['MAIS'], nlinha, m.span())
    
        elif dic['AND']:
            t = ("AND", dic['AND'], nlinha, m.span())
    
        elif dic['OR']:
            t = ("OR", dic['OR'], nlinha, m.span())
    
        elif dic['NOT']:
            t = ("NOT", dic['NOT'], nlinha, m.span())
    
        elif dic['SKIP']:
            t = ("SKIP", dic['SKIP'], nlinha, m.span())
    
        elif dic['NEWLINE']:
            t = ("NEWLINE", dic['NEWLINE'], nlinha, m.span())
    
        elif dic['ERRO']:
            t = ("ERRO", dic['ERRO'], nlinha, m.span())
    
        else:
            t = ("UNKNOWN", m.group(), nlinha, m.span())
        if not dic['SKIP'] and t[0] != 'UNKNOWN': reconhecidos.append(t)
    return reconhecidos

nlinha = 1
for linha in sys.stdin:
    for tok in tokenize(linha):
        print(tok) 
    nlinha += 1   

