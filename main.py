#!/usr/bin/env python3
"""
Compilador TurtleScript
Um compilador completo para a linguagem didática TurtleScript
que gera código Python usando Turtle Graphics.
"""

import re
import sys
from enum import Enum
from typing import List, Optional, Union, Any
from dataclasses import dataclass

# ===============================
# 1. ANÁLISE LÉXICA (LEXER)
# ===============================

class TokenType(Enum):
    # Palavras-chave
    FORWARD = "FORWARD"
    BACKWARD = "BACKWARD"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    PENUP = "PENUP"
    PENDOWN = "PENDOWN"
    REPEAT = "REPEAT"
    COLOR = "COLOR"
    SPEED = "SPEED"
    
    # Literais
    NUMBER = "NUMBER"
    STRING = "STRING"
    
    # Delimitadores
    SEMICOLON = "SEMICOLON"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    
    # Fim de arquivo
    EOF = "EOF"
    
    # Identificadores (para futuras extensões)
    IDENTIFIER = "IDENTIFIER"

@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int

class LexicalError(Exception):
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Erro léxico na linha {line}, coluna {column}: {message}")

class Lexer:
    def __init__(self, source_code: str):
        self.source = source_code
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        
        # Palavras-chave da linguagem
        self.keywords = {
            'forward': TokenType.FORWARD,
            'backward': TokenType.BACKWARD,
            'left': TokenType.LEFT,
            'right': TokenType.RIGHT,
            'penup': TokenType.PENUP,
            'pendown': TokenType.PENDOWN,
            'repeat': TokenType.REPEAT,
            'color': TokenType.COLOR,
            'speed': TokenType.SPEED,
        }
    
    def current_char(self) -> Optional[str]:
        if self.position >= len(self.source):
            return None
        return self.source[self.position]
    
    def peek_char(self) -> Optional[str]:
        peek_pos = self.position + 1
        if peek_pos >= len(self.source):
            return None
        return self.source[peek_pos]
    
    def advance(self):
        if self.position < len(self.source) and self.source[self.position] == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        self.position += 1
    
    def skip_whitespace(self):
        while self.current_char() and self.current_char().isspace():
            self.advance()
    
    def skip_comment(self):
        # Comentários de linha: // até o fim da linha
        if self.current_char() == '/' and self.peek_char() == '/':
            while self.current_char() and self.current_char() != '\n':
                self.advance()
    
    def read_number(self) -> str:
        start_column = self.column
        number = ""
        has_dot = False
        
        while self.current_char() and (self.current_char().isdigit() or self.current_char() == '.'):
            if self.current_char() == '.':
                if has_dot:
                    raise LexicalError("Número com múltiplos pontos decimais", self.line, self.column)
                has_dot = True
            number += self.current_char()
            self.advance()
        
        if number.endswith('.'):
            raise LexicalError("Número termina com ponto decimal", self.line, start_column)
        
        return number
    
    def read_string(self) -> str:
        quote_char = self.current_char()  # ' ou "
        self.advance()  # pula a primeira aspas
        string = ""
        
        while self.current_char() and self.current_char() != quote_char:
            if self.current_char() == '\\':
                self.advance()
                if self.current_char() in ['n', 't', 'r', '\\', '"', "'"]:
                    string += self.current_char()
                    self.advance()
                else:
                    raise LexicalError("Sequência de escape inválida", self.line, self.column)
            else:
                string += self.current_char()
                self.advance()
        
        if not self.current_char():
            raise LexicalError("String não fechada", self.line, self.column)
        
        self.advance()  # pula a aspas final
        return string
    
    def read_identifier(self) -> str:
        identifier = ""
        while self.current_char() and (self.current_char().isalnum() or self.current_char() == '_'):
            identifier += self.current_char()
            self.advance()
        return identifier
    
    def tokenize(self) -> List[Token]:
        while self.position < len(self.source):
            self.skip_whitespace()
            
            if not self.current_char():
                break
            
            char = self.current_char()
            current_line = self.line
            current_column = self.column
            
            # Comentários
            if char == '/' and self.peek_char() == '/':
                self.skip_comment()
                continue
            
            # Números
            elif char.isdigit():
                number = self.read_number()
                self.tokens.append(Token(TokenType.NUMBER, number, current_line, current_column))
            
            # Strings
            elif char in ['"', "'"]:
                string = self.read_string()
                self.tokens.append(Token(TokenType.STRING, string, current_line, current_column))
            
            # Identificadores e palavras-chave
            elif char.isalpha() or char == '_':
                identifier = self.read_identifier()
                token_type = self.keywords.get(identifier.lower(), TokenType.IDENTIFIER)
                self.tokens.append(Token(token_type, identifier.lower(), current_line, current_column))
            
            # Delimitadores
            elif char == ';':
                self.tokens.append(Token(TokenType.SEMICOLON, char, current_line, current_column))
                self.advance()
            elif char == '{':
                self.tokens.append(Token(TokenType.LBRACE, char, current_line, current_column))
                self.advance()
            elif char == '}':
                self.tokens.append(Token(TokenType.RBRACE, char, current_line, current_column))
                self.advance()
            elif char == '(':
                self.tokens.append(Token(TokenType.LPAREN, char, current_line, current_column))
                self.advance()
            elif char == ')':
                self.tokens.append(Token(TokenType.RPAREN, char, current_line, current_column))
                self.advance()
            
            else:
                raise LexicalError(f"Caractere inválido: '{char}'", current_line, current_column)
        
        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return self.tokens

# ===============================
# 2. ANÁLISE SINTÁTICA (PARSER)
# ===============================

@dataclass
class ASTNode:
    pass

@dataclass
class Program(ASTNode):
    statements: List[ASTNode]

@dataclass
class ForwardCommand(ASTNode):
    distance: float

@dataclass
class BackwardCommand(ASTNode):
    distance: float

@dataclass
class LeftCommand(ASTNode):
    angle: float

@dataclass
class RightCommand(ASTNode):
    angle: float

@dataclass
class PenUpCommand(ASTNode):
    pass

@dataclass
class PenDownCommand(ASTNode):
    pass

@dataclass
class ColorCommand(ASTNode):
    color: str

@dataclass
class SpeedCommand(ASTNode):
    speed: int

@dataclass
class RepeatCommand(ASTNode):
    count: int
    body: List[ASTNode]

class SyntaxError(Exception):
    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        super().__init__(f"Erro sintático na linha {token.line}, coluna {token.column}: {message}")

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0
    
    def current_token(self) -> Token:
        if self.position >= len(self.tokens):
            return self.tokens[-1]  # EOF token
        return self.tokens[self.position]
    
    def advance(self):
        if self.position < len(self.tokens) - 1:
            self.position += 1
    
    def expect(self, token_type: TokenType):
        if self.current_token().type != token_type:
            raise SyntaxError(f"Esperado {token_type.value}, encontrado {self.current_token().type.value}", 
                            self.current_token())
        token = self.current_token()
        self.advance()
        return token
    
    def parse(self) -> Program:
        statements = []
        
        while self.current_token().type != TokenType.EOF:
            stmt = self.parse_statement()
            statements.append(stmt)
        
        return Program(statements)
    
    def parse_statement(self) -> ASTNode:
        token = self.current_token()
        
        if token.type == TokenType.FORWARD:
            return self.parse_forward()
        elif token.type == TokenType.BACKWARD:
            return self.parse_backward()
        elif token.type == TokenType.LEFT:
            return self.parse_left()
        elif token.type == TokenType.RIGHT:
            return self.parse_right()
        elif token.type == TokenType.PENUP:
            return self.parse_penup()
        elif token.type == TokenType.PENDOWN:
            return self.parse_pendown()
        elif token.type == TokenType.COLOR:
            return self.parse_color()
        elif token.type == TokenType.SPEED:
            return self.parse_speed()
        elif token.type == TokenType.REPEAT:
            return self.parse_repeat()
        else:
            raise SyntaxError(f"Comando inválido: {token.value}", token)
    
    def parse_forward(self) -> ForwardCommand:
        self.expect(TokenType.FORWARD)
        distance_token = self.expect(TokenType.NUMBER)
        self.expect(TokenType.SEMICOLON)
        return ForwardCommand(float(distance_token.value))
    
    def parse_backward(self) -> BackwardCommand:
        self.expect(TokenType.BACKWARD)
        distance_token = self.expect(TokenType.NUMBER)
        self.expect(TokenType.SEMICOLON)
        return BackwardCommand(float(distance_token.value))
    
    def parse_left(self) -> LeftCommand:
        self.expect(TokenType.LEFT)
        angle_token = self.expect(TokenType.NUMBER)
        self.expect(TokenType.SEMICOLON)
        return LeftCommand(float(angle_token.value))
    
    def parse_right(self) -> RightCommand:
        self.expect(TokenType.RIGHT)
        angle_token = self.expect(TokenType.NUMBER)
        self.expect(TokenType.SEMICOLON)
        return RightCommand(float(angle_token.value))
    
    def parse_penup(self) -> PenUpCommand:
        self.expect(TokenType.PENUP)
        self.expect(TokenType.SEMICOLON)
        return PenUpCommand()
    
    def parse_pendown(self) -> PenDownCommand:
        self.expect(TokenType.PENDOWN)
        self.expect(TokenType.SEMICOLON)
        return PenDownCommand()
    
    def parse_color(self) -> ColorCommand:
        self.expect(TokenType.COLOR)
        color_token = self.expect(TokenType.STRING)
        self.expect(TokenType.SEMICOLON)
        return ColorCommand(color_token.value)
    
    def parse_speed(self) -> SpeedCommand:
        self.expect(TokenType.SPEED)
        speed_token = self.expect(TokenType.NUMBER)
        self.expect(TokenType.SEMICOLON)
        return SpeedCommand(int(float(speed_token.value)))
    
    def parse_repeat(self) -> RepeatCommand:
        self.expect(TokenType.REPEAT)
        count_token = self.expect(TokenType.NUMBER)
        self.expect(TokenType.LBRACE)
        
        body = []
        while self.current_token().type != TokenType.RBRACE:
            if self.current_token().type == TokenType.EOF:
                raise SyntaxError("Bloco repeat não fechado", self.current_token())
            stmt = self.parse_statement()
            body.append(stmt)
        
        self.expect(TokenType.RBRACE)
        return RepeatCommand(int(float(count_token.value)), body)

# ===============================
# 3. ANÁLISE SEMÂNTICA
# ===============================

class SemanticError(Exception):
    def __init__(self, message: str, node: ASTNode = None):
        self.message = message
        self.node = node
        super().__init__(f"Erro semântico: {message}")

class SemanticAnalyzer:
    def __init__(self):
        self.errors = []
    
    def analyze(self, ast: Program) -> List[str]:
        self.errors = []
        self.visit_program(ast)
        return self.errors
    
    def add_error(self, message: str):
        self.errors.append(message)
    
    def visit_program(self, node: Program):
        for stmt in node.statements:
            self.visit_statement(stmt)
    
    def visit_statement(self, node: ASTNode):
        if isinstance(node, ForwardCommand):
            self.visit_forward(node)
        elif isinstance(node, BackwardCommand):
            self.visit_backward(node)
        elif isinstance(node, LeftCommand):
            self.visit_left(node)
        elif isinstance(node, RightCommand):
            self.visit_right(node)
        elif isinstance(node, ColorCommand):
            self.visit_color(node)
        elif isinstance(node, SpeedCommand):
            self.visit_speed(node)
        elif isinstance(node, RepeatCommand):
            self.visit_repeat(node)
        # PenUp e PenDown não precisam de validação adicional
    
    def visit_forward(self, node: ForwardCommand):
        if node.distance < 0:
            self.add_error("Distância para frente não pode ser negativa")
    
    def visit_backward(self, node: BackwardCommand):
        if node.distance < 0:
            self.add_error("Distância para trás não pode ser negativa")
    
    def visit_left(self, node: LeftCommand):
        if node.angle < 0:
            self.add_error("Ângulo de rotação não pode ser negativo")
    
    def visit_right(self, node: RightCommand):
        if node.angle < 0:
            self.add_error("Ângulo de rotação não pode ser negativo")
    
    def visit_color(self, node: ColorCommand):
        valid_colors = [
            'red', 'green', 'blue', 'yellow', 'orange', 'purple', 'pink',
            'brown', 'black', 'white', 'gray', 'grey', 'cyan', 'magenta'
        ]
        if node.color.lower() not in valid_colors:
            # Verifica se é uma cor hexadecimal
            if not (node.color.startswith('#') and len(node.color) == 7 and 
                   all(c in '0123456789abcdefABCDEF' for c in node.color[1:])):
                self.add_error(f"Cor inválida: {node.color}")
    
    def visit_speed(self, node: SpeedCommand):
        if not (0 <= node.speed <= 10):
            self.add_error("Velocidade deve estar entre 0 and 10")
    
    def visit_repeat(self, node: RepeatCommand):
        if node.count <= 0:
            self.add_error("Número de repetições deve ser positivo")
        if node.count > 10000:
            self.add_error("Número de repetições muito alto (máximo 10000)")
        
        for stmt in node.body:
            self.visit_statement(stmt)

# ===============================
# 4. GERAÇÃO DE CÓDIGO
# ===============================

class CodeGenerator:
    def __init__(self):
        self.code = []
        self.indent_level = 0
    
    def generate(self, ast: Program) -> str:
        self.code = []
        self.indent_level = 0
        
        # Cabeçalho do arquivo Python
        self.emit("# Código gerado pelo compilador TurtleScript")
        self.emit("import turtle")
        self.emit("")
        self.emit("# Configuração inicial")
        self.emit("screen = turtle.Screen()")
        self.emit("screen.bgcolor('white')")
        self.emit("screen.title('TurtleScript - Resultado')")
        self.emit("")
        self.emit("t = turtle.Turtle()")
        self.emit("t.speed(6)  # Velocidade padrão")
        self.emit("")
        self.emit("# Comandos do programa")
        
        self.visit_program(ast)
        
        # Finalização
        self.emit("")
        self.emit("# Manter a janela aberta")
        self.emit("screen.exitonclick()")
        
        return '\n'.join(self.code)
    
    def emit(self, line: str):
        if line.strip():
            self.code.append('    ' * self.indent_level + line)
        else:
            self.code.append('')
    
    def visit_program(self, node: Program):
        for stmt in node.statements:
            self.visit_statement(stmt)
    
    def visit_statement(self, node: ASTNode):
        if isinstance(node, ForwardCommand):
            self.emit(f"t.forward({node.distance})")
        elif isinstance(node, BackwardCommand):
            self.emit(f"t.backward({node.distance})")
        elif isinstance(node, LeftCommand):
            self.emit(f"t.left({node.angle})")
        elif isinstance(node, RightCommand):
            self.emit(f"t.right({node.angle})")
        elif isinstance(node, PenUpCommand):
            self.emit("t.penup()")
        elif isinstance(node, PenDownCommand):
            self.emit("t.pendown()")
        elif isinstance(node, ColorCommand):
            self.emit(f"t.color('{node.color}')")
        elif isinstance(node, SpeedCommand):
            self.emit(f"t.speed({node.speed})")
        elif isinstance(node, RepeatCommand):
            self.emit(f"for _ in range({node.count}):")
            self.indent_level += 1
            for stmt in node.body:
                self.visit_statement(stmt)
            self.indent_level -= 1

# ===============================
# 5. COMPILADOR PRINCIPAL
# ===============================

class TurtleScriptCompiler:
    def __init__(self):
        self.lexer = None
        self.parser = None
        self.semantic_analyzer = SemanticAnalyzer()
        self.code_generator = CodeGenerator()
    
    def compile(self, source_code: str) -> tuple[str, List[str]]:
        """
        Compila o código TurtleScript e retorna o código Python gerado e lista de erros.
        """
        errors = []
        
        try:
            # 1. Análise Léxica
            self.lexer = Lexer(source_code)
            tokens = self.lexer.tokenize()
            
            # 2. Análise Sintática
            self.parser = Parser(tokens)
            ast = self.parser.parse()
            
            # 3. Análise Semântica
            semantic_errors = self.semantic_analyzer.analyze(ast)
            if semantic_errors:
                return "", semantic_errors
            
            # 4. Geração de Código
            python_code = self.code_generator.generate(ast)
            
            return python_code, []
            
        except (LexicalError, SyntaxError, SemanticError) as e:
            return "", [str(e)]
        except Exception as e:
            return "", [f"Erro interno do compilador: {str(e)}"]
    
    def compile_file(self, input_file: str, output_file: str = None) -> bool:
        """
        Compila um arquivo TurtleScript e salva o resultado em um arquivo Python.
        """
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            python_code, errors = self.compile(source_code)
            
            if errors:
                print("Erros encontrados durante a compilação:")
                for error in errors:
                    print(f"  {error}")
                return False
            
            if output_file is None:
                output_file = input_file.replace('.ts', '.py')
                if output_file == input_file:
                    output_file = input_file + '.py'
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(python_code)
            
            print(f"Compilação bem-sucedida! Arquivo gerado: {output_file}")
            return True
            
        except FileNotFoundError:
            print(f"Erro: Arquivo '{input_file}' não encontrado.")
            return False
        except Exception as e:
            print(f"Erro durante a compilação: {str(e)}")
            return False

# ===============================
# 6. INTERFACE DE LINHA DE COMANDO
# ===============================

def main():
    if len(sys.argv) < 2:
        print("Uso: python turtlescript_compiler.py <arquivo.ts> [arquivo_saida.py]")
        print("\nExemplo de código TurtleScript:")
        print("""
// Exemplo: Desenhar um quadrado
repeat 4 {
    forward 100;
    right 90;
}

// Exemplo: Desenhar uma estrela colorida
color "red";
repeat 5 {
    forward 100;
    right 144;
}
        """)
        return
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    compiler = TurtleScriptCompiler()
    success = compiler.compile_file(input_file, output_file)
    
    if success:
        print("\nPara executar o programa gerado:")
        output_name = output_file or input_file.replace('.ts', '.py')
        print(f"python {output_name}")

if __name__ == "__main__":
    main()

# ===============================
# 7. EXEMPLO DE USO PROGRAMÁTICO
# ===============================

def exemplo_uso():
    """Exemplo de como usar o compilador programaticamente"""
    
    # Código de exemplo em TurtleScript
    codigo_turtlescript = """
    // Desenhar um hexágono colorido
    color "blue";
    speed 8;
    
    repeat 6 {
        forward 100;
        right 60;
    }
    
    // Mover para uma nova posição
    penup;
    forward 150;
    pendown;
    
    // Desenhar um triângulo
    color "red";
    repeat 3 {
        forward 80;
        left 120;
    }
    """
    
    # Compilar o código
    compiler = TurtleScriptCompiler()
    codigo_python, erros = compiler.compile(codigo_turtlescript)
    
    if erros:
        print("Erros encontrados:")
        for erro in erros:
            print(f"  {erro}")
    else:
        print("Código Python gerado:")
        print(codigo_python)

# Executar exemplo se o arquivo for executado diretamente
if __name__ == "__main__" and len(sys.argv) == 1:
    exemplo_uso()