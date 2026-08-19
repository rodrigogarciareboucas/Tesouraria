# -*- coding: utf-8 -*-
import sqlite3
from datetime import date

DB_PATH = r'C:\Users\Rodrigo  Garcia\Desktop\Maconaria\financas_loja.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Simular a lógica do relatório de inadimplência
hoje = date.today()
meses_analise = []

# Para "Últimos 3 meses"
for i in range(3):
    mes = hoje.month - i - 1
    ano = hoje.year
    if mes <= 0:
        mes += 12
        ano -= 1
    meses_analise.append((ano, mes))

print("=== Meses analisados (Últimos 3 meses) ===")
for ano, mes in meses_analise:
    print(f"Ano: {ano}, Mês: {mes}")

print("\n=== Verificação de obreiros não isentos ===")
cursor.execute("SELECT id, nome, cim, isento FROM obreiros")
obreiros = cursor.fetchall()

meses_ingles = {
    1: 'January', 2: 'February', 3: 'March', 4: 'April',
    5: 'May', 6: 'June', 7: 'July', 8: 'August',
    9: 'September', 10: 'October', 11: 'November', 12: 'December'
}

for obreiro_id, nome, cim, isento in obreiros:
    if isento == 1:
        continue
    
    print(f"\n--- {nome} (ID: {obreiro_id}, CIM: {cim}) ---")
    pagou_algum_mes = False
    
    for ano, mes in meses_analise:
        mes_ingles = meses_ingles[mes]
        
        cursor.execute("""
            SELECT COUNT(*) FROM transacoes
            WHERE obreiro_id = ? 
            AND categoria = 'Mensalidade Loja'
            AND ano_competencia = ?
            AND mes_competencia = ?
        """, (obreiro_id, str(ano), mes_ingles))
        
        count = cursor.fetchone()[0]
        status = "✓ PAGOU" if count > 0 else "✗ NÃO PAGOU"
        print(f"  {ano}/{mes} ({mes_ingles}): {count} transações - {status}")
        
        if count > 0:
            pagou_algum_mes = True
    
    if not pagou_algum_mes:
        print(f"  >>> INADIMPLENTE")
    else:
        print(f"  >>> REGULAR")

conn.close()
