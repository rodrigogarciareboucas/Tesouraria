import sqlite3

conn = sqlite3.connect(r'c:\Users\Rodrigo  Garcia\Desktop\Maconaria\financas_loja.db')
cursor = conn.cursor()

print("=== Adicionando colunas à tabela transacoes ===")
try:
    cursor.execute("ALTER TABLE transacoes ADD COLUMN mes_competencia TEXT")
    print("  ✓ mes_competencia adicionada")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("  - mes_competencia já existe")
    else:
        print(f"  ✗ Erro: {e}")

try:
    cursor.execute("ALTER TABLE transacoes ADD COLUMN ano_competencia TEXT")
    print("  ✓ ano_competencia adicionada")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("  - ano_competencia já existe")
    else:
        print(f"  ✗ Erro: {e}")

print("\n=== Adicionando colunas à tabela obreiros ===")
try:
    cursor.execute("ALTER TABLE obreiros ADD COLUMN cim TEXT DEFAULT '000000'")
    print("  ✓ cim adicionada")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("  - cim já existe")
    else:
        print(f"  ✗ Erro: {e}")

try:
    cursor.execute("ALTER TABLE obreiros ADD COLUMN isento INTEGER DEFAULT 0")
    print("  ✓ isento adicionada")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("  - isento já existe")
    else:
        print(f"  ✗ Erro: {e}")

try:
    cursor.execute("ALTER TABLE obreiros ADD COLUMN data_admissao TEXT DEFAULT '2026-01-01'")
    print("  ✓ data_admissao adicionada")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("  - data_admissao já existe")
    else:
        print(f"  ✗ Erro: {e}")

# Migrar dados de status_isento para isento se necessário
cursor.execute("SELECT COUNT(*) FROM obreiros WHERE status_isento IS NOT NULL")
if cursor.fetchone()[0] > 0:
    cursor.execute("UPDATE obreiros SET isento = status_isento WHERE isento = 0")
    print("  ✓ Dados migrados de status_isento para isento")

conn.commit()
conn.close()
print("\n=== Atualização concluída ===")
