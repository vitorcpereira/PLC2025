import re

def cabecalhos(text):
    res = re.sub(r'(###)\s(.+)', fr"<h3>\2</h3>", text)
    if res == text:
        res = re.sub(r'(##)\s(.+)', fr"<h2>\2</h2>", text)
        if res == text:
            res = re.sub(r'(#)\s(.+)', fr"<h1>\2</h1>", text)
    return res


def bold(text):
    return re.sub(r'\*\*(.+)\*\*', r'<b>\1</b>', text)

def italico(text):
    return re.sub(r'\*(.+)\*', r'<i>\1</i>', text)

def listanumerada(text):
    res = "<ol>\n"
    res += re.sub(r'\d+\.\s(.+)\b', r'<li>\1</li>',text)
    res += "\n</ol>"
    return res

def link(text):
    return re.sub(r'([^!]+)\[(.+)\]\((.+)\)', r'\1 <a href="\3">\2</a>',text)


def imagem(text):
    return re.sub(r'\!\[(.+)\]\((.+)\)', r'<img src="\2" alt="\1"/>',text)

def markdown_to_html(markdown_text):
    html_text = listanumerada(markdown_text)
    
    lines = html_text.split('\n')
    res = []
    
    for line in lines:
        if not line.strip().startswith('<li>'):
            line = cabecalhos(line)
        
        line = bold(line)
        line = italico(line)
        line = link(line)
        line = imagem(line)
        
        res.append(line)
    
    return '\n'.join(res)

ex = """## Exemplo
**Como pode ser consultado em [pagina da UC](http://www.uc.pt)**
![imagem dum coelho](http://www.coellho.com)"""
print(markdown_to_html(ex))
