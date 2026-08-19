# -*- coding: utf-8 -*-
import sqlite3

DB_PATH = r'C:\Users\Rodrigo  Garcia\Desktop\Maconaria\financas_loja.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=== Verificação da Migração ===\n")

# Contar obreiros
cursor.execute("SELECT COUNT(*) FROM obreiros")
obreiros_count = cursor.fetchone()[0]
print(f"Total de obreiros: {obreiros_count}")

# Contar transações
cursor.execute("SELECT COUNT(*) FROM transacoes")
transacoes_count = cursor.fetchone()[0]
print(f"Total de transações: {transacoes_count}")

# Contar categorias
cursor.execute("SELECT COUNT(*) FROM categorias")
categorias_count = cursor.fetchone()[0]
print(f"Total de categorias: {categorias_count}")

# Mostrar alguns obreiros
print("\n=== Primeiros 5 obreiros ===")
cursor.execute("SELECT id, nome, cim, grau, valor_mensalidade FROM obreiros LIMIT 5")
for row in cursor.fetchall():
    print(f"  ID: {row[0]}, Nome: {row[1]}, CIM: {row[2]}, Grau: {row[3]}, Mensalidade: R$ {row[4]:.2f}")

# Mostrar algumas transações
print("\n=== Primeiras 5 transações ===")
cursor.execute("SELECT id, data, tipo, categoria, valor FROM transacoes LIMIT 5")
for row in cursor.fetchall():
    print(f"  ID: {row[0]}, Data: {row[1]}, Tipo: {row[2]}, Categoria: {row[3]}, Valor: R$ {row[4]:.2f}")

# Mostrar categorias
print("\n=== Categorias ===")
cursor.execute("SELECT nome FROM categorias")
for row in cursor.fetchall():
    print(f"  - {row[0]}")

conn.close()

print("\n=== Verificação concluída ===")
