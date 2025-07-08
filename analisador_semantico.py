class AnalisadorSemantico:
    def __init__(self):
        self.tabela_simbolos = {}
        self.tipos_validos = ['inteiro', 'real', 'texto', 'logico']

    def analisar(self, ast):
        try:
            self.verificar_no(ast)
            print("Análise semântica concluída com sucesso!")
        except Exception as e:
            raise Exception(f"Erro semântico: {str(e)}")

    def verificar_no(self, no):
        if not no:
            return
        
        metodos = {
            'Programa': lambda: self.verificar_filhos(no),
            'Declaracao': lambda: self.verificar_declaracao(no),
            'Atribuicao': lambda: self.verificar_atribuicao(no),
            'Movimento': lambda: self.verificar_movimento(no),
            'ComandoCaneta': lambda: self.verificar_comando_caneta(no),
            'ComandoTela': lambda: self.verificar_comando_tela(no),
            'ComandoTurtle': lambda: self.verificar_comando_turtle(no),
            'Condicional': lambda: self.verificar_condicional(no),
            'Repeticao': lambda: self.verificar_repeticao(no),
            'Enquanto': lambda: self.verificar_enquanto(no),
            'ExpressaoAritmetica': lambda: self.verificar_expressao_aritmetica(no),
            'ExpressaoLogica': lambda: self.verificar_expressao_logica(no)
        }
        
        if no.tipo in metodos:
            metodos[no.tipo]()
        else:
            self.verificar_filhos(no)

    def verificar_filhos(self, no):
        for filho in no.filhos:
            self.verificar_no(filho)

    def verificar_declaracao(self, no):
        tipo = no.valor['tipo']
        variaveis = no.valor['variaveis']
        
        if tipo not in self.tipos_validos:
            raise Exception(f"tipo '{tipo}' não é válido. Tipos válidos: {self.tipos_validos}")
        
        for var in variaveis:
            if var in self.tabela_simbolos:
                raise Exception(f"variável '{var}' já foi declarada")
            self.tabela_simbolos[var] = tipo

    def verificar_atribuicao(self, no):
        var = no.valor['ident']
        valor = no.valor['valor']
        
        if var not in self.tabela_simbolos:
            raise Exception(f"variável '{var}' não foi declarada")
        
        tipo_var = self.tabela_simbolos[var]
        tipo_valor = self.inferir_tipo(valor)
        
        if not self.tipos_compativeis(tipo_var, tipo_valor):
            raise Exception(f"não é possível atribuir {tipo_valor} à variável '{var}' do tipo {tipo_var}")

    def verificar_movimento(self, no):
        comando = no.valor['comando']
        
        if comando == 'ir_para':
            self.verificar_tipo_numerico(no.valor['x'], 'coordenada x')
            self.verificar_tipo_numerico(no.valor['y'], 'coordenada y')
        else:
            self.verificar_tipo_numerico(no.valor['valor'], f"argumento do comando '{comando}'")

    def verificar_comando_caneta(self, no):
        comando = no.valor['comando']
        
        if comando in ['levantar_caneta', 'abaixar_caneta']:
            return
        elif comando == 'definir_cor':
            self.verificar_tipo_especifico(no.valor['valor'], 'texto', f"argumento do comando '{comando}'")
        elif comando == 'definir_espessura':
            self.verificar_tipo_numerico(no.valor['valor'], f"argumento do comando '{comando}'")

    def verificar_comando_tela(self, no):
        comando = no.valor['comando']
        
        if comando == 'limpar_tela':
            return
        elif comando == 'cor_de_fundo':
            self.verificar_tipo_especifico(no.valor['valor'], 'texto', f"argumento do comando '{comando}'")

    def verificar_comando_turtle(self, no):
        comando = no.valor['comando']
        
        if comando == 'velocidade':
            tipo_valor = self.inferir_tipo(no.valor['valor'])
            if not self.eh_tipo_numerico(tipo_valor):
                raise Exception(f"argumento do comando '{comando}' deve ser numérico, encontrado {tipo_valor}")
            
            valor = no.valor['valor']
            if isinstance(valor, str) and valor.isdigit():
                val_int = int(valor)
                if val_int < 0 or val_int > 10:
                    raise Exception(f"velocidade deve estar entre 0 e 10, encontrado {val_int}")
        
        elif comando == 'circulo':
            self.verificar_tipo_numerico(no.valor['valor'], f"raio do comando '{comando}'")


    def verificar_condicional(self, no):
        self.verificar_tipo_especifico(no.valor['condicao'], 'logico', 'condição do se')
        self.verificar_filhos(no)

    def verificar_repeticao(self, no):
        vezes = no.valor['vezes']
        
        if isinstance(vezes, str):
            if vezes.isdigit():
                if int(vezes) <= 0:
                    raise Exception(f"número de repetições deve ser positivo, encontrado {vezes}")
            elif vezes not in self.tabela_simbolos:
                raise Exception(f"variável '{vezes}' não foi declarada")
            elif self.tabela_simbolos[vezes] != 'inteiro':
                raise Exception(f"variável '{vezes}' deve ser do tipo inteiro")
        
        self.verificar_tipo_especifico(vezes, 'inteiro', 'número de repetições')
        self.verificar_filhos(no)

    def verificar_enquanto(self, no):
        self.verificar_tipo_especifico(no.valor['condicao'], 'logico', 'condição do enquanto')
        self.verificar_filhos(no)

    def verificar_expressao_aritmetica(self, no):
        operador = no.valor.get('operador')
        
        if operador:
            self.verificar_tipo_numerico(no.valor['esquerda'], 'operando esquerdo')
            self.verificar_tipo_numerico(no.valor['direita'], 'operando direito')
        else:
            valor = no.valor.get('valor')
            if valor:
                self.verificar_tipo_numerico(valor, 'valor')

    def verificar_expressao_logica(self, no):
        operador = no.valor.get('operador')
        
        if operador in ['&&', '||']:
            self.verificar_tipo_especifico(no.valor['esquerda'], 'logico', 'operando esquerdo')
            self.verificar_tipo_especifico(no.valor['direita'], 'logico', 'operando direito')
        elif operador == '!':
            self.verificar_tipo_especifico(no.valor.get('operando'), 'logico', 'operando do !')
        elif operador in ['==', '!=', '<', '>', '<=', '>=']:
            tipo_esq = self.inferir_tipo(no.valor['esquerda'])
            tipo_dir = self.inferir_tipo(no.valor['direita'])
            
            if not self.tipos_compativeis(tipo_esq, tipo_dir):
                raise Exception(f"não é possível comparar {tipo_esq} com {tipo_dir}")

    def verificar_tipo_numerico(self, valor, contexto):
        tipo = self.inferir_tipo(valor)
        if not self.eh_tipo_numerico(tipo):
            raise Exception(f"{contexto} deve ser numérico, encontrado {tipo}")

    def verificar_tipo_especifico(self, valor, tipo_esperado, contexto):
        tipo = self.inferir_tipo(valor)
        if tipo != tipo_esperado:
            raise Exception(f"{contexto} deve ser {tipo_esperado}, encontrado {tipo}")

    def inferir_tipo(self, valor):
        if hasattr(valor, 'tipo'):
            return 'real' if valor.tipo == 'ExpressaoAritmetica' else 'logico'
        
        if isinstance(valor, dict):
            if valor.get('tipo') == 'ExpressaoAritmetica':
                return 'real'
            elif valor.get('tipo') == 'ExpressaoLogica':
                return 'logico'
            elif valor.get('tipo') == 'Identificador':
                return self.obter_tipo_variavel(valor.get('nome'))
        
        if isinstance(valor, str):
            if valor in self.tabela_simbolos:
                return self.tabela_simbolos[valor]
            elif valor.isdigit() or (valor.startswith('-') and valor[1:].isdigit()):
                return 'inteiro'
            elif self.eh_real(valor):
                return 'real'
            elif valor.startswith('"') and valor.endswith('"'):
                return 'texto'
            elif valor.lower() in ['verdadeiro', 'falso']:
                return 'logico'
            else:
                raise Exception(f"variável '{valor}' não foi declarada")
        
        if isinstance(valor, (int, float)):
            return 'inteiro' if isinstance(valor, int) else 'real'
        
        if isinstance(valor, bool):
            return 'logico'
        
        raise Exception(f"tipo de valor desconhecido: {type(valor)} - {valor}")

    def obter_tipo_variavel(self, nome):
        if nome in self.tabela_simbolos:
            return self.tabela_simbolos[nome]
        else:
            raise Exception(f"variável '{nome}' não foi declarada")

    def eh_real(self, valor):
        try:
            float(valor)
            return '.' in valor
        except ValueError:
            return False

    def eh_tipo_numerico(self, tipo):
        return tipo in ['inteiro', 'real']

    def tipos_compativeis(self, tipo1, tipo2):
        if tipo1 == tipo2:
            return True
        return (tipo1 == 'inteiro' and tipo2 == 'real') or (tipo1 == 'real' and tipo2 == 'inteiro')