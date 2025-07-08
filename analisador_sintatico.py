class NoAST:
    def __init__(self, tipo, valor=None):
        self.tipo = tipo
        self.valor = valor
        self.filhos = []

    def adicionar_filho(self, filho):
        self.filhos.append(filho)

    def __repr__(self):
        return f"{self.tipo}({self.valor}) -> {self.filhos}"

class AnalisadorSintatico:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def token_atual(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consumir(self, tipo_esperado=None, valor_esperado=None):
        token = self.token_atual()
        if not token:
            raise Exception("Erro sintático: fim inesperado do arquivo")
        
        if tipo_esperado and token.tipo != tipo_esperado:
            raise Exception(f"Erro sintático na linha {token.linha}: esperado {tipo_esperado}, encontrado {token.tipo}")
        
        if valor_esperado and token.valor != valor_esperado:
            raise Exception(f"Erro sintático na linha {token.linha}: esperado '{valor_esperado}', encontrado '{token.valor}'")
        
        self.pos += 1
        return token

    def programa(self):
        no = NoAST("Programa")
        self.consumir('RESERVADA', 'inicio')
        
        while self.token_atual() and self.token_atual().valor != 'fim':
            no.adicionar_filho(self.comando())
        
        self.consumir('RESERVADA', 'fim')
        return no

    def comando(self):
        token = self.token_atual()
        if not token:
            raise Exception("Erro sintático: comando esperado")
        
        if token.valor == 'var':
            return self.declaracao_variavel()
        elif token.valor == 'se':
            return self.condicional()
        elif token.valor == 'repita':
            return self.repeticao_repita()
        elif token.valor == 'enquanto':
            return self.repeticao_enquanto()
        elif token.tipo == 'IDENTIFICADOR':
            return self.atribuicao()
        elif token.valor in ['avancar', 'recuar', 'girar_direita', 'girar_esquerda', 'ir_para']:
            return self.movimento()
        elif token.valor in ['levantar_caneta', 'abaixar_caneta', 'definir_cor', 'definir_espessura']:
            return self.comando_caneta()
        elif token.valor in ['cor_de_fundo', 'limpar_tela']:
            return self.comando_tela()
        elif token.valor in ['velocidade', 'circulo']:
            return self.comando_turtle()
        else:
            raise Exception(f"Erro sintático na linha {token.linha}: comando inválido '{token.valor}'")

    def declaracao_variavel(self):
        self.consumir('RESERVADA', 'var')
        tipo = self.consumir('RESERVADA')
        
        ids = [self.consumir('IDENTIFICADOR').valor]
        while self.token_atual() and self.token_atual().valor == ',':
            self.consumir('SIMBOLO', ',')
            ids.append(self.consumir('IDENTIFICADOR').valor)
        
        self.consumir('SIMBOLO', ';')
        return NoAST('Declaracao', {'tipo': tipo.valor, 'variaveis': ids})

    def atribuicao(self):
        ident = self.consumir('IDENTIFICADOR')
        self.consumir('OPERADOR_ATRIBUICAO', '=')
        valor = self.expressao()
        self.consumir('SIMBOLO', ';')
        return NoAST('Atribuicao', {'ident': ident.valor, 'valor': valor})

    def movimento(self):
        comando = self.consumir('RESERVADA')
        
        if comando.valor == 'ir_para':
            self.consumir('SIMBOLO', '(')
            x = self.expressao()
            self.consumir('SIMBOLO', ',')
            y = self.expressao()
            self.consumir('SIMBOLO', ')')
            self.consumir('SIMBOLO', ';')
            return NoAST('Movimento', {'comando': comando.valor, 'x': x, 'y': y})
        
        valor = self.expressao()
        self.consumir('SIMBOLO', ';')
        return NoAST('Movimento', {'comando': comando.valor, 'valor': valor})

    def comando_caneta(self):
        comando = self.consumir('RESERVADA')
        
        if comando.valor in ['levantar_caneta', 'abaixar_caneta']:
            self.consumir('SIMBOLO', ';')
            return NoAST('ComandoCaneta', {'comando': comando.valor})
        
        valor = self.expressao()
        self.consumir('SIMBOLO', ';')
        return NoAST('ComandoCaneta', {'comando': comando.valor, 'valor': valor})

    def comando_tela(self):
        comando = self.consumir('RESERVADA')
        
        if comando.valor == 'limpar_tela':
            self.consumir('SIMBOLO', ';')
            return NoAST('ComandoTela', {'comando': comando.valor})
        
        valor = self.expressao()
        self.consumir('SIMBOLO', ';')
        return NoAST('ComandoTela', {'comando': comando.valor, 'valor': valor})

    def comando_turtle(self):
        comando = self.consumir('RESERVADA')
        
        valor = self.expressao()
        self.consumir('SIMBOLO', ';')
        return NoAST('ComandoTurtle', {'comando': comando.valor, 'valor': valor})

    def condicional(self):
        self.consumir('RESERVADA', 'se')
        condicao = self.expressao()
        self.consumir('RESERVADA', 'entao')

        no = NoAST('Condicional', {'condicao': condicao})
        
        bloco_verdadeiro = NoAST('BlocoVerdadeiro')
        while self.token_atual() and self.token_atual().valor not in ['senao', 'fim_se']:
            bloco_verdadeiro.adicionar_filho(self.comando())
        no.adicionar_filho(bloco_verdadeiro)

        if self.token_atual() and self.token_atual().valor == 'senao':
            self.consumir('RESERVADA', 'senao')
            bloco_falso = NoAST('BlocoFalso')
            while self.token_atual() and self.token_atual().valor != 'fim_se':
                bloco_falso.adicionar_filho(self.comando())
            no.adicionar_filho(bloco_falso)

        self.consumir('RESERVADA', 'fim_se')
        return no

    def repeticao_repita(self):
        self.consumir('RESERVADA', 'repita')
        vezes = self.expressao()
        self.consumir('RESERVADA', 'vezes')

        no = NoAST('Repeticao', {'vezes': vezes})
        while self.token_atual() and self.token_atual().valor != 'fim_repita':
            no.adicionar_filho(self.comando())

        self.consumir('RESERVADA', 'fim_repita')
        return no
    
    def repeticao_enquanto(self):
        self.consumir('RESERVADA', 'enquanto')
        condicao = self.expressao()
        self.consumir('RESERVADA', 'faca')
        
        no = NoAST('Enquanto', {'condicao': condicao})
        while self.token_atual() and self.token_atual().valor != 'fim_enquanto':
            no.adicionar_filho(self.comando())
        
        self.consumir('RESERVADA', 'fim_enquanto')
        return no

    def expressao(self):
        return self.expressao_logica() if self.eh_expressao_logica() else self.expressao_aritmetica()

    def eh_expressao_logica(self):
        pos_original = self.pos
        
        while self.pos < len(self.tokens) and self.tokens[self.pos].valor not in [';', 'entao', 'faca', 'vezes']:
            if self.tokens[self.pos].tipo == 'OPERADOR_LOGICO':
                self.pos = pos_original
                return True
            self.pos += 1
        
        self.pos = pos_original
        return False

    def expressao_logica(self):
        esquerda = self.termo_logico()
        
        while (self.token_atual() and 
               self.token_atual().tipo == 'OPERADOR_LOGICO' and
               self.token_atual().valor in ['&&', '||']):
            op = self.consumir('OPERADOR_LOGICO')
            direita = self.termo_logico()
            esquerda = NoAST('ExpressaoLogica', {
                'operador': op.valor,
                'esquerda': esquerda,
                'direita': direita
            })
        
        return esquerda

    def termo_logico(self):
        if self.token_atual() and self.token_atual().valor == '!':
            op = self.consumir('OPERADOR_LOGICO', '!')
            fator = self.fator_logico()
            return NoAST('ExpressaoLogica', {
                'operador': op.valor,
                'operando': fator
            })
        
        return self.comparacao()

    def comparacao(self):
        esquerda = self.expressao_aritmetica()
        
        if (self.token_atual() and 
            self.token_atual().tipo == 'OPERADOR_LOGICO' and
            self.token_atual().valor in ['==', '!=', '<', '<=', '>', '>=']):
            op = self.consumir('OPERADOR_LOGICO')
            direita = self.expressao_aritmetica()
            return NoAST('ExpressaoLogica', {
                'operador': op.valor,
                'esquerda': esquerda,
                'direita': direita
            })
        
        return esquerda

    def expressao_aritmetica(self):
        esquerda = self.termo_aritmetico()
        
        while (self.token_atual() and 
               self.token_atual().tipo == 'OPERADOR_ARITMETICO' and
               self.token_atual().valor in ['+', '-']):
            op = self.consumir('OPERADOR_ARITMETICO')
            direita = self.termo_aritmetico()
            esquerda = NoAST('ExpressaoAritmetica', {
                'operador': op.valor,
                'esquerda': esquerda,
                'direita': direita
            })
        
        return esquerda

    def termo_aritmetico(self):
        esquerda = self.fator_aritmetico()
        
        while (self.token_atual() and 
               self.token_atual().tipo == 'OPERADOR_ARITMETICO' and
               self.token_atual().valor in ['*', '/', '%']):
            op = self.consumir('OPERADOR_ARITMETICO')
            direita = self.fator_aritmetico()
            esquerda = NoAST('ExpressaoAritmetica', {
                'operador': op.valor,
                'esquerda': esquerda,
                'direita': direita
            })
        
        return esquerda

    def fator_aritmetico(self):
        token = self.token_atual()
        
        if not token:
            raise Exception("Erro sintático: fator aritmético esperado")
        
        if token.tipo == 'IDENTIFICADOR':
            return self.consumir('IDENTIFICADOR').valor
        elif token.tipo in ['INTEIRO', 'REAL', 'STRING']:
            return self.consumir(token.tipo).valor
        elif token.tipo == 'RESERVADA' and token.valor in ['verdadeiro', 'falso']:
            return self.consumir('RESERVADA').valor
        elif token.valor == '(':
            self.consumir('SIMBOLO', '(')
            expr = self.expressao_aritmetica()
            self.consumir('SIMBOLO', ')')
            return expr
        elif token.valor in ['+', '-'] and token.tipo == 'OPERADOR_ARITMETICO':
            op = self.consumir('OPERADOR_ARITMETICO')
            fator = self.fator_aritmetico()
            return f"{op.valor}{fator}"
        else:
            raise Exception(f"Erro sintático na linha {token.linha}: fator aritmético inválido '{token.valor}'")

    def fator_logico(self):
        token = self.token_atual()
        
        if not token:
            raise Exception("Erro sintático: fator lógico esperado")
        
        if token.tipo == 'IDENTIFICADOR':
            return self.consumir('IDENTIFICADOR').valor
        elif token.tipo == 'RESERVADA' and token.valor in ['verdadeiro', 'falso']:
            return self.consumir('RESERVADA').valor
        elif token.valor == '(':
            self.consumir('SIMBOLO', '(')
            expr = self.expressao_logica()
            self.consumir('SIMBOLO', ')')
            return expr
        else:
            raise Exception(f"Erro sintático na linha {token.linha}: fator lógico inválido '{token.valor}'")