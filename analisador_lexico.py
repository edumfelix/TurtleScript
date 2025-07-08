import re

class Token:
    def __init__(self, tipo, valor, linha):
        self.tipo = tipo
        self.valor = valor
        self.linha = linha

    def __repr__(self):
        return f"<{self.tipo}, {self.valor}, linha {self.linha}>"

class AnalisadorLexico:
    def __init__(self, codigo):
        self.codigo = codigo
        self.tokens = []
        self.linha_atual = 1
        self.padrao_tokens = [
            (r'\b(inicio|fim|var|inteiro|real|texto|logico|verdadeiro|falso)\b', 'RESERVADA'),
            (r'\b(se|entao|senao|fim_se)\b', 'RESERVADA'),
            (r'\b(repita|vezes|fim_repita)\b', 'RESERVADA'),
            (r'\b(enquanto|faca|fim_enquanto)\b', 'RESERVADA'),
            (r'\b(avancar|recuar|girar_direita|girar_esquerda|ir_para)\b', 'RESERVADA'),
            (r'\b(levantar_caneta|abaixar_caneta|definir_cor|definir_espessura)\b', 'RESERVADA'),
            (r'\b(cor_de_fundo|limpar_tela)\b', 'RESERVADA'),
            (r'\b(velocidade|circulo)\b', 'RESERVADA'),
            (r'//.*', 'COMENTARIO'),
            (r'"[^"]*"', 'STRING'),
            (r"'[^']*'", 'STRING'),
            (r'[0-9]+\.[0-9]+', 'REAL'),
            (r'[0-9]+', 'INTEIRO'),
            (r'[a-zA-Z_][a-zA-Z0-9_]*', 'IDENTIFICADOR'),
            (r'==|!=|<=|>=|<|>|&&|\|\||!', 'OPERADOR_LOGICO'),
            (r'\+|-|\*|/|%', 'OPERADOR_ARITMETICO'),
            (r'=', 'OPERADOR_ATRIBUICAO'),
            (r'\(|\)|,|;', 'SIMBOLO'),
            (r'\s+', None),
        ]

    def analisar(self):
        pos = 0
        
        while pos < len(self.codigo):
            matched = False
            
            for padrao, tipo in self.padrao_tokens:
                resultado = re.match(padrao, self.codigo[pos:])
                
                if resultado:
                    texto = resultado.group(0)
                    
                    if tipo == 'COMENTARIO':
                        self.linha_atual += texto.count('\n')
                    elif tipo:
                        self.tokens.append(Token(tipo, texto, self.linha_atual))
                    
                    self.linha_atual += texto.count('\n')
                    pos += len(texto)
                    matched = True
                    break
            
            if not matched:
                raise Exception(f"Erro léxico na linha {self.linha_atual}: caractere inesperado '{self.codigo[pos]}'")
                
        return self.tokens

    def imprimir_tokens(self):
        for token in self.tokens:
            print(token)