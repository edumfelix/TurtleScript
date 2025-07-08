import turtle

tela = turtle.Screen()
t = turtle.Turtle()

x = 0
y = 0
passo = 0
condicao = False
fator = 0.0
nome = ''
x = 0
y = 0
passo = 10
condicao = True
fator = 1.5
nome = "Teste"
if condicao:
    t.forward(passo)
    t.right(90)
else:
    t.backward(passo)
    t.left(90)
for _i_2889021532688 in range(int(4)):
    t.forward(passo)
    t.right(90)
while (x < 50):
    t.forward(passo)
    x = (x + passo)
t.penup()
t.goto(100, 100)
t.pendown()
t.pencolor("blue")
t.pensize(2)
tela.bgcolor("yellow")
t.clear()