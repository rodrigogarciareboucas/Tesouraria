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

# String de conexão do Pooler do Supabase (porta 6543 - recomendado para aplicações na nuvem)
DATABASE_URL = "postgresql://postgres.umlwznpctkdzhghhpjgk:a4kaGf7zYmiq6CAP@aws-0-us-east-1.pooler.supabase.com:6543/postgres"

# Configurações do Pooler do Supabase para psycopg2
POSTGRES_CONFIG = {
    'host': 'aws-0-us-east-1.pooler.supabase.com',
    'port': 6543,
    'database': 'postgres',
    'user': 'postgres.umlwznpctkdzhghhpjgk',
    'password': 'a4kaGf7zYmiq6CAP',
}
