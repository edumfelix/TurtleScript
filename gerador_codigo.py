import sys
import os

class GeradorCodigo:
    def __init__(self):
        self.variaveis_declaradas = {}
        self.indent_level = 0
        self.linhas = []
        
    def gerar_codigo(self, ast):
        self.linhas = [
            "import turtle",
            "",
            "tela = turtle.Screen()",
            "t = turtle.Turtle()",
            "",        
        ]
        self.processar_comandos(ast.filhos)
        return "\n".join(self.linhas)
        
    def get_indent(self):
        return "    " * self.indent_level
    
    def adicionar_linha(self, linha):
        if linha.strip():
            self.linhas.append(self.get_indent() + linha)
        else:
            self.linhas.append("")
    
    def processar_comandos(self, comandos):
        for comando in comandos:
            self.processar_comando(comando)
    
    def processar_comando(self, comando):
        if comando.tipo == 'Declaracao':
            self.processar_declaracao(comando)
        elif comando.tipo == 'Atribuicao':
            self.processar_atribuicao(comando)
        elif comando.tipo == 'Movimento':
            self.processar_movimento(comando)
        elif comando.tipo == 'ComandoCaneta':
            self.processar_comando_caneta(comando)
        elif comando.tipo == 'ComandoTela':
            self.processar_comando_tela(comando)
        elif comando.tipo == 'ComandoTurtle':
            self.processar_comando_turtle(comando)
        elif comando.tipo == 'Condicional':
            self.processar_condicional(comando)
        elif comando.tipo == 'Repeticao':
            self.processar_repeticao(comando)
        elif comando.tipo == 'Enquanto':
            self.processar_enquanto(comando)
        else:
            if hasattr(comando, 'filhos'):
                self.processar_comandos(comando.filhos)
    
    def processar_declaracao(self, comando):
        tipo = comando.valor['tipo']
        variaveis = comando.valor['variaveis']
        
        for var in variaveis:
            self.variaveis_declaradas[var] = tipo
            
            if tipo == 'inteiro':
                self.adicionar_linha(f"{var} = 0")
            elif tipo == 'real':
                self.adicionar_linha(f"{var} = 0.0")
            elif tipo == 'texto':
                self.adicionar_linha(f"{var} = ''")
            elif tipo == 'logico':
                self.adicionar_linha(f"{var} = False")
    
    def processar_atribuicao(self, comando):
        ident = comando.valor['ident']
        valor = self.processar_expressao(comando.valor['valor'])
        
        if ident in self.variaveis_declaradas:
            tipo = self.variaveis_declaradas[ident]
            if tipo == 'logico':
                self.adicionar_linha(f"{ident} = {valor}")
            else:
                self.adicionar_linha(f"{ident} = {valor}")
        else:
            self.adicionar_linha(f"{ident} = {valor}")
    
    def processar_movimento(self, comando):
        cmd = comando.valor['comando']
        
        if cmd == 'ir_para':
            x = self.processar_expressao(comando.valor['x'])
            y = self.processar_expressao(comando.valor['y'])
            self.adicionar_linha(f"t.goto({x}, {y})")
        else:
            valor = self.processar_expressao(comando.valor['valor'])
            
            if cmd == 'avancar':
                self.adicionar_linha(f"t.forward({valor})")
            elif cmd == 'recuar':
                self.adicionar_linha(f"t.backward({valor})")
            elif cmd == 'girar_direita':
                self.adicionar_linha(f"t.right({valor})")
            elif cmd == 'girar_esquerda':
                self.adicionar_linha(f"t.left({valor})")
    
    def processar_comando_caneta(self, comando):
        cmd = comando.valor['comando']
        
        if cmd == 'levantar_caneta':
            self.adicionar_linha("t.penup()")
        elif cmd == 'abaixar_caneta':
            self.adicionar_linha("t.pendown()")
        elif cmd == 'definir_cor':
            valor = self.processar_expressao(comando.valor['valor'])
            self.adicionar_linha(f"t.pencolor({valor})")
        elif cmd == 'definir_espessura':
            valor = self.processar_expressao(comando.valor['valor'])
            self.adicionar_linha(f"t.pensize({valor})")
    
    def processar_comando_tela(self, comando):
        cmd = comando.valor['comando']
        
        if cmd == 'limpar_tela':
            self.adicionar_linha("t.clear()")
        elif cmd == 'cor_de_fundo':
            valor = self.processar_expressao(comando.valor['valor'])
            self.adicionar_linha(f"tela.bgcolor({valor})")

    def processar_comando_turtle(self, comando):
        cmd = comando.valor['comando']
        
        if cmd == 'velocidade':
            valor = self.processar_expressao(comando.valor['valor'])
            self.adicionar_linha(f"t.speed({valor})")
        elif cmd == 'circulo':
            raio = self.processar_expressao(comando.valor['valor'])
            self.adicionar_linha(f"t.circle({raio})")
    
    def processar_condicional(self, comando):
        condicao = self.processar_expressao(comando.valor['condicao'])
        self.adicionar_linha(f"if {condicao}:")
        
        bloco_verdadeiro = None
        bloco_falso = None
        
        for filho in comando.filhos:
            if filho.tipo == 'BlocoVerdadeiro':
                bloco_verdadeiro = filho
            elif filho.tipo == 'BlocoFalso':
                bloco_falso = filho
        
        if bloco_verdadeiro:
            self.indent_level += 1
            if bloco_verdadeiro.filhos:
                self.processar_comandos(bloco_verdadeiro.filhos)
            else:
                self.adicionar_linha("pass")
            self.indent_level -= 1
        else:
            self.indent_level += 1
            self.adicionar_linha("pass")
            self.indent_level -= 1
        
        if bloco_falso:
            self.adicionar_linha("else:")
            self.indent_level += 1
            if bloco_falso.filhos:
                self.processar_comandos(bloco_falso.filhos)
            else:
                self.adicionar_linha("pass")
            self.indent_level -= 1
    
    def processar_repeticao(self, comando):
        vezes = self.processar_expressao(comando.valor['vezes'])
        contador = f"_i_{id(comando)}"
        
        self.adicionar_linha(f"for {contador} in range(int({vezes})):")
        
        self.indent_level += 1
        if comando.filhos:
            self.processar_comandos(comando.filhos)
        else:
            self.adicionar_linha("pass")
        self.indent_level -= 1
    
    def processar_enquanto(self, comando):
        condicao = self.processar_expressao(comando.valor['condicao'])
        self.adicionar_linha(f"while {condicao}:")
        
        self.indent_level += 1
        if comando.filhos:
            self.processar_comandos(comando.filhos)
        else:
            self.adicionar_linha("pass")
        self.indent_level -= 1
    
    def processar_expressao(self, expr):
        if isinstance(expr, str):
            if expr.startswith('"') and expr.endswith('"'):
                return expr  
            elif expr.startswith("'") and expr.endswith("'"):
                return f'"{expr[1:-1]}"'  
            elif expr.lower() in ['verdadeiro', 'falso']:
                return 'True' if expr.lower() == 'verdadeiro' else 'False'
            elif expr.replace('.', '').replace('-', '').isdigit():
                return expr  
            else:
                return expr  
        
        elif isinstance(expr, dict):
            if expr.get('tipo') == 'ExpressaoAritmetica':
                return self.processar_expressao_aritmetica(expr)
            elif expr.get('tipo') == 'ExpressaoLogica':
                return self.processar_expressao_logica(expr)
            elif expr.get('tipo') == 'Identificador':
                return expr.get('nome', '')
        
        elif hasattr(expr, 'tipo'):
            if expr.tipo == 'ExpressaoAritmetica':
                return self.processar_expressao_aritmetica(expr.valor)
            elif expr.tipo == 'ExpressaoLogica':
                return self.processar_expressao_logica(expr.valor)
        
        return str(expr)
    
    def processar_expressao_aritmetica(self, expr_info):
        if isinstance(expr_info, dict) and 'operador' in expr_info:
            op = expr_info['operador']
            esq = self.processar_expressao(expr_info['esquerda'])
            dir = self.processar_expressao(expr_info['direita'])
            
            if op == '%':
                return f"({esq} % {dir})"
            else:
                return f"({esq} {op} {dir})"
        
        return str(expr_info)
    
    def processar_expressao_logica(self, expr_info):
        if isinstance(expr_info, dict) and 'operador' in expr_info:
            op = expr_info['operador']
            
            if op == '!' or op == 'nao':
                operando = self.processar_expressao(expr_info.get('operando', expr_info.get('valor')))
                return f"(not {operando})"
            
            else:
                esq = self.processar_expressao(expr_info['esquerda'])
                dir = self.processar_expressao(expr_info['direita'])
                
                if op == '&&' or op == 'e':
                    return f"({esq} and {dir})"
                elif op == '||' or op == 'ou':
                    return f"({esq} or {dir})"
                elif op == '==':
                    return f"({esq} == {dir})"
                elif op == '!=':
                    return f"({esq} != {dir})"
                elif op in ['<', '>', '<=', '>=']:
                    return f"({esq} {op} {dir})"
        
        return str(expr_info)


def gerar_codigo(ast):
    gerador = GeradorCodigo()
    return gerador.gerar_codigo(ast)


def main():
    if len(sys.argv) < 2:
        print("Uso: python gerador_codigo.py <arquivo_entrada> [arquivo_saida]")
        print("Exemplo: python gerador_codigo.py programa.txt")
        sys.exit(1)
    
    nome_entrada = sys.argv[1]
    
    if len(sys.argv) >= 3:
        nome_saida = sys.argv[2]
    else:
        base_name = os.path.splitext(os.path.basename(nome_entrada))[0]
        nome_saida = f"saida_{base_name}.py"
    
    if not os.path.exists(nome_entrada):
        print(f"Erro: Arquivo '{nome_entrada}' não encontrado!")
        sys.exit(1)
    
    try:
        from analisador_lexico import AnalisadorLexico
        from analisador_sintatico import AnalisadorSintatico
        from analisador_semantico import AnalisadorSemantico
        
        with open(nome_entrada, "r", encoding="utf-8") as f:
            codigo = f.read()
        
        print(f"Analisando arquivo: {nome_entrada}")
        
        print("Realizando análise léxica...")
        lexer = AnalisadorLexico(codigo)
        tokens = lexer.analisar()
        print(f"{len(tokens)} tokens encontrados")
        
        print("Realizando análise sintática...")
        parser = AnalisadorSintatico(tokens)
        ast = parser.programa()
        print("Análise sintática concluída")
        
        print("Realizando análise semântica...")
        semantic_analyzer = AnalisadorSemantico()
        semantic_analyzer.analisar(ast)
        print("Análise semântica concluída")
        
        print("Gerando código Python...")
        codigo_python = gerar_codigo(ast)
        
        with open(f"saidas/{nome_saida}", "w", encoding="utf-8") as f:
            f.write(codigo_python)
        
        print(f"Código Python gerado com sucesso: {nome_saida}")
        print(f"Execute com: python {nome_saida}")
        
    except Exception as e:
        print(f"Erro durante a compilação: {e}")
        import traceback
    
if __name__ == "__main__":
    main()
