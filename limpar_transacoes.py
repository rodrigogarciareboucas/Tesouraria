# -*- coding: utf-8 -*-
import sqlite3
import shutil
from datetime import datetime
import os

DB_PATH = r'C:\Users\Rodrigo  Garcia\Desktop\Maconaria\financas_loja.db'
BKP_DIR = r'C:\Users\Rodrigo  Garcia\Desktop\Maconaria\BKP'
os.makedirs(BKP_DIR, exist_ok=True)
BACKUP_PATH = os.path.join(BKP_DIR, f'financas_loja_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')

print("=== LIMPEZA DE TRANSAÇÕES ===\n")

# Criar backup antes de limpar
print("1. Criando backup do banco de dados...")
try:
    shutil.copy2(DB_PATH, BACKUP_PATH)
    print(f"   ✅ Backup criado em: {BACKUP_PATH}")
except Exception as e:
    print(f"   ❌ Erro ao criar backup: {e}")
    exit(1)

# Conectar ao banco
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Contar transações antes de limpar
cursor.execute("SELECT COUNT(*) FROM transacoes")
total_transacoes = cursor.fetchone()[0]
print(f"\n2. Total de transações encontradas: {total_transacoes}")

# Contar por tipo
cursor.execute("SELECT tipo, COUNT(*) FROM transacoes GROUP BY tipo")
tipos = cursor.fetchall()
print("   Por tipo:")
for tipo, count in tipos:
    print(f"   - {tipo}: {count}")

# Confirmar limpeza
print("\n⚠️  ATENÇÃO: Isso apagará TODAS as transações (entradas e saídas)")
print("   Os obreiros, categorias e outros dados serão mantidos.")
confirmacao = input("\nDigite 'SIM' para confirmar a limpeza: ")

if confirmacao.upper() == 'SIM':
    print("\n3. Limpando tabela de transações...")
    cursor.execute("DELETE FROM transacoes")
    conn.commit()
    
    print(f"   ✅ {cursor.rowcount} transações removidas")
    
    # Verificar se está vazio
    cursor.execute("SELECT COUNT(*) FROM transacoes")
    restantes = cursor.fetchone()[0]
    print(f"   Transações restantes: {restantes}")
    
    conn.close()
    print("\n✅ Limpeza concluída com sucesso!")
    print(f"   Backup disponível em: {BACKUP_PATH}")
else:
    print("\n❌ Limpeza cancelada pelo usuário.")
    conn.close()
