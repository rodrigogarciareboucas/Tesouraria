# -*- coding: utf-8 -*-
"""
Script para migrar dados do PostgreSQL local para Supabase
"""
import psycopg2
import sys

# Configuração PostgreSQL Local
LOCAL_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'financas_loja',
    'user': 'postgres',
    'password': 'postgres',
}

# Configuração Supabase (Pooler - porta 6543)
from config_postgres import POSTGRES_CONFIG as SUPABASE_CONFIG

def migrar_tabela(conn_origem, conn_destino, nome_tabela):
    """Migra dados de uma tabela"""
    print(f"\n📦 Migrando tabela: {nome_tabela}")

    try:
        cursor_origem = conn_origem.cursor()
        cursor_destino = conn_destino.cursor()

        # Obter dados da origem
        cursor_origem.execute(f"SELECT * FROM {nome_tabela}")
        rows = cursor_origem.fetchall()
        col_names = [desc[0] for desc in cursor_origem.description]

        if not rows:
            print(f"   ℹ️  Tabela vazia, pulando...")
            return

        print(f"   📊 {len(rows)} registros encontrados")

        # Inserir no destino
        for row in rows:
            placeholders = ', '.join(['%s'] * len(row))
            columns = ', '.join(col_names)
            query = f"INSERT INTO {nome_tabela} ({columns}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"

            try:
                cursor_destino.execute(query, row)
            except Exception as e:
                print(f"   ⚠️  Erro ao inserir registro: {e}")
                continue

        conn_destino.commit()
        print(f"   ✅ Migração concluída")

        cursor_origem.close()
        cursor_destino.close()

    except Exception as e:
        print(f"   ❌ Erro ao migrar tabela {nome_tabela}: {e}")
        raise

def criar_tabelas_supabase(conn):
    """Cria as tabelas no Supabase usando a estrutura do database_config.py"""
    print("\n🔨 Criando tabelas no Supabase...")

    cursor = conn.cursor()

    # Drop tabelas existentes para recriar com estrutura correta
    tabelas_drop = [
        'parcelas',
        'agendamentos_pagamentos',
        'fila_sicredi',
        'usuarios',
        'eventos',
        'noticias',
        'transacoes',
        'categorias',
        'obreiros'
    ]

    for tabela in tabelas_drop:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {tabela} CASCADE")
            print(f"   🗑️  Tabela {tabela} removida")
        except Exception as e:
            print(f"   ⚠️  Erro ao remover {tabela}: {e}")

    conn.commit()

    # Tabela de Obreiros
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS obreiros (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            grau TEXT NOT NULL,
            valor_mensalidade REAL NOT NULL,
            status_isento INTEGER DEFAULT 0,
            cim TEXT DEFAULT '000000',
            isento INTEGER DEFAULT 0,
            data_admissao TEXT DEFAULT '2026-01-01',
            status TEXT,
            data_nascimento TEXT,
            email TEXT,
            telefone TEXT,
            endereco TEXT
        )
    """)

    # Tabela de Categorias
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL UNIQUE
        )
    """)

    # Tabela de Transações
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transacoes (
            id SERIAL PRIMARY KEY,
            data TEXT NOT NULL,
            tipo TEXT NOT NULL,
            categoria TEXT,
            descricao TEXT,
            valor REAL NOT NULL,
            mes_competencia TEXT,
            ano_competencia TEXT,
            tipo_caixa TEXT,
            obreiro_id INTEGER,
            evento_id INTEGER,
            id_sicredi TEXT
        )
    """)

    # Tabela de Notícias
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS noticias (
            id SERIAL PRIMARY KEY,
            titulo TEXT NOT NULL,
            conteudo TEXT,
            data_publicacao TEXT,
            autor TEXT,
            ativo INTEGER DEFAULT 1
        )
    """)

    # Tabela de Eventos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS eventos (
            id SERIAL PRIMARY KEY,
            titulo TEXT NOT NULL,
            descricao TEXT,
            data_evento TEXT,
            hora TEXT,
            local TEXT,
            tipo TEXT
        )
    """)

    # Tabela de Usuários
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL,
            nivel_acesso TEXT,
            ativo INTEGER DEFAULT 1,
            data_cadastro TEXT
        )
    """)

    # Tabela de Fila Sicredi
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fila_sicredi (
            id SERIAL PRIMARY KEY,
            id_sicredi TEXT,
            data TEXT,
            tipo TEXT,
            descricao_banco TEXT,
            valor REAL,
            status_conciliacao TEXT DEFAULT 'Pendente'
        )
    """)

    # Tabela de Agendamentos de Pagamentos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agendamentos_pagamentos (
            id SERIAL PRIMARY KEY,
            descricao TEXT NOT NULL,
            valor_total REAL NOT NULL,
            numero_parcelas INTEGER NOT NULL,
            data_primeira_parcela TEXT,
            intervalo_dias INTEGER DEFAULT 30,
            status TEXT DEFAULT 'Pendente',
            data_criacao TEXT,
            observacoes TEXT
        )
    """)

    # Tabela de Parcelas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parcelas (
            id SERIAL PRIMARY KEY,
            agendamento_id INTEGER,
            numero_parcela INTEGER,
            valor_parcela REAL,
            data_vencimento TEXT,
            status TEXT DEFAULT 'Pendente',
            data_pagamento TEXT
        )
    """)

    conn.commit()
    print("✅ Tabelas criadas com sucesso!")
    cursor.close()

def main():
    print("=" * 60)
    print("🚀 MIGRAÇÃO POSTGRESQL LOCAL → SUPABASE")
    print("=" * 60)

    # Conectar ao PostgreSQL local
    print("\n🔌 Conectando ao PostgreSQL local...")
    try:
        conn_local = psycopg2.connect(**LOCAL_CONFIG)
        print("✅ Conectado ao PostgreSQL local")
    except Exception as e:
        print(f"❌ Erro ao conectar ao PostgreSQL local: {e}")
        sys.exit(1)

    # Conectar ao Supabase
    print("\n🔌 Conectando ao Supabase...")
    try:
        conn_supabase = psycopg2.connect(**SUPABASE_CONFIG, sslmode='require')
        print("✅ Conectado ao Supabase")
    except Exception as e:
        print(f"❌ Erro ao conectar ao Supabase: {e}")
        sys.exit(1)

    # Criar tabelas no Supabase
    criar_tabelas_supabase(conn_supabase)

    # Lista de tabelas para migrar
    tabelas = [
        'obreiros',
        'categorias',
        'transacoes',
        'noticias',
        'eventos',
        'usuarios',
        'fila_sicredi',
        'agendamentos_pagamentos',
        'parcelas'
    ]

    # Migrar cada tabela
    for tabela in tabelas:
        try:
            migrar_tabela(conn_local, conn_supabase, tabela)
        except Exception as e:
            print(f"❌ Erro fatal ao migrar {tabela}: {e}")
            continue

    # Reajustar sequences: dados migrados com IDs explícitos deixam o
    # nextval desatualizado, causando "duplicate key" em futuros INSERTs
    print("\n🔧 Reajustando sequences...")
    cursor_seq = conn_supabase.cursor()
    for tabela in tabelas:
        cursor_seq.execute(
            "SELECT setval(pg_get_serial_sequence(%s, 'id'), "
            "COALESCE((SELECT MAX(id) FROM " + tabela + "), 1))",
            (tabela,)
        )
    conn_supabase.commit()
    cursor_seq.close()
    print("✅ Sequences reajustadas")

    # Fechar conexões
    conn_local.close()
    conn_supabase.close()

    print("\n" + "=" * 60)
    print("✅ MIGRAÇÃO CONCLUÍDA!")
    print("=" * 60)

if __name__ == "__main__":
    main()
