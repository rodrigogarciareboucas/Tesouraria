import sqlite3

conn = sqlite3.connect(r'c:\Users\Rodrigo  Garcia\Desktop\Maconaria\financas_loja.db')
cursor = conn.cursor()

print("=== Estrutura da tabela transacoes ===")
cursor.execute("PRAGMA table_info(transacoes)")
colunas = cursor.fetchall()
for col in colunas:
    print(f"  {col[1]}: {col[2]}")

print("\n=== Estrutura da tabela obreiros ===")
cursor.execute("PRAGMA table_info(obreiros)")
colunas = cursor.fetchall()
for col in colunas:
    print(f"  {col[1]}: {col[2]}")

print("\n=== Estrutura da tabela categorias ===")
cursor.execute("PRAGMA table_info(categorias)")
colunas = cursor.fetchall()
for col in colunas:
    print(f"  {col[1]}: {col[2]}")

conn.close()
