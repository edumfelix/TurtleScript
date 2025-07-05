# Código gerado pelo compilador TurtleScript
import turtle

# Configuração inicial
screen = turtle.Screen()
screen.bgcolor('white')
screen.title('TurtleScript - Resultado')

t = turtle.Turtle()
t.speed(6)  # Velocidade padrão

# Comandos do programa
t.speed(5)
for _ in range(8):
    t.color('red')
    for _ in range(4):
        t.forward(30.0)
        t.right(90.0)
    t.right(45.0)

# Manter a janela aberta
screen.exitonclick()