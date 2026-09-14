# -*- coding: utf-8 -*-
"""
Backup completo do banco Supabase (PostgreSQL) para arquivo .sql
Gera DROP + CREATE + INSERTs + reajuste de sequences.
Uso: python backup_supabase.py
"""
import os
from datetime import datetime
from database_config import get_connection
from config_postgres import POSTGRES_CONFIG

BACKUP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backup')
os.makedirs(BACKUP_DIR, exist_ok=True)

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
backup_path = os.path.join(BACKUP_DIR, f"supabase_backup_{timestamp}.sql")

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
    SELECT table_name FROM information_schema.tables
    WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
    ORDER BY table_name
""")
tabelas = [row[0] for row in cursor.fetchall()]

sql = f"-- Backup PostgreSQL (Supabase) - {timestamp}\n"
sql += f"-- Database: {POSTGRES_CONFIG['database']} | Host: {POSTGRES_CONFIG['host']}\n"
sql += "SET client_encoding = 'UTF8';\n\n"

for tabela in tabelas:
    print(f"Exportando {tabela}...")
    sql += f"DROP TABLE IF EXISTS {tabela} CASCADE;\n"

    cursor.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = %s
        ORDER BY ordinal_position
    """, (tabela,))
    colunas = cursor.fetchall()

    sql += f"CREATE TABLE {tabela} (\n"
    col_defs = []
    for col_name, data_type, is_nullable, col_default in colunas:
        col_def = f"    {col_name} {data_type}"
        if col_default:
            col_def += f" DEFAULT {col_default}"
        if is_nullable == 'NO':
            col_def += " NOT NULL"
        col_defs.append(col_def)
    sql += ",\n".join(col_defs)
    sql += "\n);\n\n"

    cursor.execute(f"SELECT * FROM {tabela}")
    rows = cursor.fetchall()
    col_names = [desc[0] for desc in cursor.description]

    for row in rows:
        values = []
        for val in row:
            if val is None:
                values.append('NULL')
            elif isinstance(val, str):
                values.append("'" + val.replace("'", "''") + "'")
            elif isinstance(val, (int, float)):
                values.append(str(val))
            elif isinstance(val, bool):
                values.append('TRUE' if val else 'FALSE')
            else:
                values.append("'" + str(val) + "'")
        sql += f"INSERT INTO {tabela} ({', '.join(col_names)}) VALUES ({', '.join(values)});\n"
    sql += "\n"
    print(f"  {len(rows)} registros")

# Reajustar sequences ao final do restore (evita duplicate key apos import com IDs explicitos)
sql += "-- Reajuste de sequences\n"
for tabela in tabelas:
    sql += (f"SELECT setval(pg_get_serial_sequence('{tabela}', 'id'), "
            f"COALESCE((SELECT MAX(id) FROM {tabela}), 1));\n")

cursor.close()
conn.close()

with open(backup_path, 'w', encoding='utf-8') as f:
    f.write(sql)

tamanho_kb = os.path.getsize(backup_path) / 1024
print(f"\nBackup salvo: {backup_path}")
print(f"Tamanho: {tamanho_kb:.2f} KB | Tabelas: {len(tabelas)}")
