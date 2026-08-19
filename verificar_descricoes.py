import sqlite3

conn = sqlite3.connect('financas_loja.db')
cursor = conn.cursor()

# Buscar algumas transações de mensalidade para ver o formato
cursor.execute("SELECT * FROM transacoes WHERE descricao LIKE '%Mensalidade Loja%' LIMIT 10")
transacoes = cursor.fetchall()

print("Transações de Mensalidade Loja (amostra):")
for t in transacoes:
    print(f"  Descrição: {t[3]}")
    print(f"  Obreiro ID: {t[5]}")
    print(f"  Valor: {t[4]}")
    print()

# Buscar obreiros e verificar se têm transações
cursor.execute("SELECT id, nome FROM obreiros WHERE isento = 0 LIMIT 5")
obreiros = cursor.fetchall()

print("\nVerificação de obreiros:")
for o in obreiros:
    obreiro_id = o[0]
    obreiro_nome = o[1]
    
    # Tentar buscar por obreiro_id
    cursor.execute("SELECT COUNT(*) FROM transacoes WHERE obreiro_id = ? AND descricao LIKE '%Mensalidade Loja%'", (obreiro_id,))
    count_id = cursor.fetchone()[0]
    
    # Tentar buscar por nome na descrição
    cursor.execute("SELECT COUNT(*) FROM transacoes WHERE descricao LIKE ? AND descricao LIKE '%Mensalidade Loja%'", (f'%{obreiro_nome}%',))
    count_nome = cursor.fetchone()[0]
    
    print(f"  {obreiro_nome} (ID {obreiro_id}):")
    print(f"    Por obreiro_id: {count_id}")
    print(f"    Por nome na descrição: {count_nome}")

conn.close()
