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

# Tentar usar st.secrets (Streamlit Cloud)
try:
    import streamlit as st
    # Se estiver no Streamlit Cloud, usar st.secrets
    if hasattr(st, 'secrets'):
        POSTGRES_CONFIG = {
            'host': st.secrets.get('POSTGRES_HOST', 'db.umlwznpctkdzhghhpjgk.supabase.co'),
            'port': int(st.secrets.get('POSTGRES_PORT', 5432)),
            'database': st.secrets.get('POSTGRES_DATABASE', 'postgres'),
            'user': st.secrets.get('POSTGRES_USER', 'postgres'),
            'password': st.secrets.get('POSTGRES_PASSWORD', 'a4kaGf7zYmiq6CAP'),
        }
        sslmode = st.secrets.get('POSTGRES_SSLMODE', 'require')
    else:
        # Usar variáveis de ambiente locais
        POSTGRES_CONFIG = {
            'host': os.getenv('POSTGRES_HOST', 'db.umlwznpctkdzhghhpjgk.supabase.co'),
            'port': int(os.getenv('POSTGRES_PORT', 5432)),
            'database': os.getenv('POSTGRES_DATABASE', 'postgres'),
            'user': os.getenv('POSTGRES_USER', 'postgres'),
            'password': os.getenv('POSTGRES_PASSWORD', 'a4kaGf7zYmiq6CAP'),
        }
        sslmode = os.getenv('POSTGRES_SSLMODE', 'require')
except ImportError:
    # Se streamlit não estiver disponível, usar variáveis de ambiente
    POSTGRES_CONFIG = {
        'host': os.getenv('POSTGRES_HOST', 'db.umlwznpctkdzhghhpjgk.supabase.co'),
        'port': int(os.getenv('POSTGRES_PORT', 5432)),
        'database': os.getenv('POSTGRES_DATABASE', 'postgres'),
        'user': os.getenv('POSTGRES_USER', 'postgres'),
        'password': os.getenv('POSTGRES_PASSWORD', 'a4kaGf7zYmiq6CAP'),
    }
    sslmode = os.getenv('POSTGRES_SSLMODE', 'require')

# String de conexão (com SSL para Supabase)
DATABASE_URL = f"postgresql://{POSTGRES_CONFIG['user']}:{POSTGRES_CONFIG['password']}@{POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}/{POSTGRES_CONFIG['database']}?sslmode={sslmode}"
