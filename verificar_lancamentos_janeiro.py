# -*- coding: utf-8 -*-
import sqlite3
from datetime import date

DB_PATH = r'C:\Users\Rodrigo  Garcia\Desktop\Maconaria\financas_loja.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=== VERIFICAÇÃO DE LANÇAMENTOS DE JANEIRO ===\n")

# Verificar todos os lançamentos de janeiro/2026
cursor.execute("""
    SELECT id, data, tipo, categoria, descricao, valor, obreiro_id, mes_competencia, ano_competencia
    FROM transacoes
    WHERE (mes_competencia = 'January' OR mes_competencia = 'Janeiro') 
    AND ano_competencia = '2026'
    ORDER BY data DESC
""")

lancamentos_janeiro = cursor.fetchall()

print(f"Total de lançamentos de janeiro/2026: {len(lancamentos_janeiro)}\n")

if lancamentos_janeiro:
    for lanc in lancamentos_janeiro:
        id_, data, tipo, cat, desc, val, obreiro_id, mes_comp, ano_comp = lanc
        print(f"ID: {id_}")
        print(f"  Data: {data}")
        print(f"  Tipo: '{tipo}'")
        print(f"  Categoria: {cat}")
        print(f"  Descrição: {desc}")
        print(f"  Valor: R$ {val:.2f}")
        print(f"  Obreiro ID: {obreiro_id}")
        print(f"  Mês Competência: {mes_comp}")
        print(f"  Ano Competência: {ano_comp}")
        print()
else:
    print("Nenhum lançamento encontrado para janeiro/2026")

# Verificar lançamentos com obreiro_id (lançamentos da carteira)
print("\n=== LANÇAMENTOS COM OBREIRO_ID (CARTEIRA) ===\n")
cursor.execute("""
    SELECT id, data, tipo, categoria, descricao, valor, obreiro_id, mes_competencia, ano_competencia
    FROM transacoes
    WHERE obreiro_id IS NOT NULL
    ORDER BY data DESC
    LIMIT 20
""")

lancamentos_obreiro = cursor.fetchall()
print(f"Total de lançamentos com obreiro_id: {len(lancamentos_obreiro)}\n")

if lancamentos_obreiro:
    for lanc in lancamentos_obreiro:
        id_, data, tipo, cat, desc, val, obreiro_id, mes_comp, ano_comp = lanc
        print(f"ID: {id_} | Data: {data} | Tipo: '{tipo}' | Cat: {cat} | Valor: R$ {val:.2f} | Obreiro: {obreiro_id}")
else:
    print("Nenhum lançamento com obreiro_id encontrado")

# Verificar tipos de lançamentos existentes
print("\n=== TIPOS DE LANÇAMENTOS NO BANCO ===\n")
cursor.execute("SELECT DISTINCT tipo FROM transacoes")
tipos = cursor.fetchall()
for tipo in tipos:
    print(f"Tipo: '{tipo[0]}'")

conn.close()
