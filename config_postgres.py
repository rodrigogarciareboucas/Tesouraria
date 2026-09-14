# -*- coding: utf-8 -*-
"""
Configuração de Banco de Dados PostgreSQL
Sistema Financeiro - Loja Jerônimo Rosado 1994
"""

import os
from dotenv import load_dotenv

# Tentar carregar variáveis de ambiente do arquivo .env
try:
    load_dotenv()
except:
    pass  # Ignorar erro se .env não existir ou estiver corrompido

# Configurações do PostgreSQL (lê de variáveis de ambiente ou usa valores padrão do Supabase)
POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'db.umlwznpctkdzhghhpjgk.supabase.co'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'database': os.getenv('POSTGRES_DATABASE', 'postgres'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'a4kaGf7zYmiq6CAP'),
}

# String de conexão (com SSL para Supabase)
sslmode = os.getenv('POSTGRES_SSLMODE', 'require')
DATABASE_URL = f"postgresql://{POSTGRES_CONFIG['user']}:{POSTGRES_CONFIG['password']}@{POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}/{POSTGRES_CONFIG['database']}?sslmode={sslmode}"
