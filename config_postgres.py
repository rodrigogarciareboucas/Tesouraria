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

# String de conexão direta do Supabase (sem SSL - SSL foi desmarcado nas configurações)
DATABASE_URL = "postgresql://postgres:a4kaGf7zYmiq6CAP@db.umlwznpctkdzhghhpjgk.supabase.co:5432/postgres"

# Configurações do Supabase para psycopg2
POSTGRES_CONFIG = {
    'host': 'db.umlwznpctkdzhghhpjgk.supabase.co',
    'port': 5432,
    'database': 'postgres',
    'user': 'postgres',
    'password': 'a4kaGf7zYmiq6CAP',
}
