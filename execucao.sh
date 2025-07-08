#!/bin/bash

for entrada in entradas/entrada*.txt; do
  echo "Processando $entrada..."
  python3 gerador_codigo.py "$entrada"
done
for saida in saidas/saida_entrada*.py; do
  echo "Iniciando $saida..."
  python3 "$saida"
done
