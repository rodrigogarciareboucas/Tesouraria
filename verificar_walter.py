import sqlite3

conn = sqlite3.connect('financas_loja.db')
cursor = conn.cursor()

# Verificar estrutura da tabela transações
cursor.execute("PRAGMA table_info(transacoes)")
colunas = cursor.fetchall()
print("Estrutura da tabela transacoes:")
for col in colunas:
    print(f"  {col[1]}: {col[2]}")

print("\n" + "="*50)

# Buscar transações com descrição contendo "Mensalidade Loja"
cursor.execute("SELECT * FROM transacoes WHERE descricao LIKE '%Mensalidade Loja%' AND descricao LIKE '%WALTER%'")
transacoes = cursor.fetchall()
print(f"\nTransações com 'Mensalidade Loja' e 'WALTER': {len(transacoes)}")

if transacoes:
    print("\nTransações encontradas:")
    for t in transacoes:
        print(f"  ID: {t[0]}, Data: {t[1]}, Categoria: {t[2]}, Descrição: {t[3]}, Valor: {t[4]}, Obreiro ID: {t[5]}")

print("\n" + "="*50)

# Verificar obreiros duplicados
cursor.execute("SELECT id, nome FROM obreiros WHERE nome = 'WALTER QUEIROZ XAVIER'")
obreiros_duplicados = cursor.fetchall()
print(f"\nObreiros com nome 'WALTER QUEIROZ XAVIER': {len(obreiros_duplicados)}")
for o in obreiros_duplicados:
    print(f"  ID: {o[0]}")

conn.close()
