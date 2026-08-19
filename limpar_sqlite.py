# -*- coding: utf-8 -*-
import sqlite3

DB_PATH = r'C:\Users\Rodrigo  Garcia\Desktop\Maconaria\financas_loja.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=== Limpando dados do SQLite ===")

# Limpar transações
cursor.execute("DELETE FROM transacoes")
print(f"✓ Transações limpas: {cursor.rowcount}")

# Limpar obreiros
cursor.execute("DELETE FROM obreiros")
print(f"✓ Obreiros limpos: {cursor.rowcount}")

# Limpar categorias
cursor.execute("DELETE FROM categorias")
print(f"✓ Categorias limpas: {cursor.rowcount}")

conn.commit()
conn.close()

print("=== Limpeza concluída ===")
