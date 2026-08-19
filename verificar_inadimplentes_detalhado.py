# -*- coding: utf-8 -*-
import sqlite3
from datetime import date

DB_PATH = r'C:\Users\Rodrigo  Garcia\Desktop\Maconaria\financas_loja.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Verificar os obreiros que foram marcados como inadimplentes
print("=== OBRERIROS MARCADOS COMO INADIMPLENTES ===\n")

# Obreiros que apareceram como inadimplentes no teste anterior
obreiros_verificar = [199, 214, 216]

for obreiro_id in obreiros_verificar:
    cursor.execute("SELECT nome, cim, isento FROM obreiros WHERE id = ?", (obreiro_id,))
    resultado = cursor.fetchone()
    
    if resultado:
        nome, cim, isento = resultado
        print(f"--- {nome} (ID: {obreiro_id}, CIM: {cim}, Isento: {isento}) ---")
        
        # Verificar TODAS as transações deste obreiro
        cursor.execute("""
            SELECT data, tipo, categoria, valor, mes_competencia, ano_competencia
            FROM transacoes
            WHERE obreiro_id = ?
            ORDER BY data DESC
        """, (obreiro_id,))
        
        transacoes = cursor.fetchall()
        print(f"Total de transações: {len(transacoes)}")
        
        if transacoes:
            for trans in transacoes:
                print(f"  Data: {trans[0]}, Tipo: {trans[1]}, Categoria: {trans[2]}, Valor: R$ {trans[3]:.2f}, Mês: {trans[4]}, Ano: {trans[5]}")
        else:
            print("  Nenhuma transação encontrada")
        print()

# Verificar também se há algum obreiro recentemente cadastrado
print("\n=== OBRERIROS RECENTEMENTE CADASTRADOS (últimos 5 IDs) ===")
cursor.execute("SELECT id, nome, cim, isento FROM obreiros ORDER BY id DESC LIMIT 5")
recentes = cursor.fetchall()

for obreiro_id, nome, cim, isento in recentes:
    print(f"ID: {obreiro_id}, Nome: {nome}, CIM: {cim}, Isento: {isento}")
    
    # Verificar transações
    cursor.execute("""
        SELECT COUNT(*) FROM transacoes WHERE obreiro_id = ?
    """, (obreiro_id,))
    count = cursor.fetchone()[0]
    print(f"  Transações: {count}")

conn.close()
