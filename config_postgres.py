# -*- coding: utf-8 -*-
"""
Configuração de Banco de Dados PostgreSQL
Sistema Financeiro - Loja Jerônimo Rosado 1994

A senha NÃO fica no código. Configure DATABASE_URL em:
- Local: arquivo .env
- Streamlit Cloud: Settings > Secrets
"""

import os
from urllib.parse import urlparse, unquote
from dotenv import load_dotenv

# Tentar carregar variáveis de ambiente do arquivo .env
try:
    load_dotenv()
except:
    pass  # Ignorar erro se .env não existir ou estiver corrompido

# 1) DATABASE_URL direto (local .env ou secret da nuvem)
DATABASE_URL = os.getenv("DATABASE_URL")

# 2) Montar a partir de POSTGRES_* (legado)
if not DATABASE_URL and os.getenv("POSTGRES_HOST"):
    DATABASE_URL = (
        f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
        f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT', '6543')}"
        f"/{os.getenv('POSTGRES_DATABASE', 'postgres')}"
    )

# 3) st.secrets (Streamlit Cloud)
if not DATABASE_URL:
    try:
        import streamlit as st
        DATABASE_URL = st.secrets.get("DATABASE_URL")
    except Exception:
        DATABASE_URL = None

# Configurações para psycopg2 (derivadas da DATABASE_URL)
if DATABASE_URL:
    _u = urlparse(DATABASE_URL)
    POSTGRES_CONFIG = {
        'host': _u.hostname,
        'port': _u.port or 5432,
        'database': _u.path.lstrip('/'),
        'user': unquote(_u.username or ''),
        'password': unquote(_u.password or ''),
    }
else:
    POSTGRES_CONFIG = None
