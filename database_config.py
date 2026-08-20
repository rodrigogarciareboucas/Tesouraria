# -*- coding: utf-8 -*-
"""
Módulo de Configuração do Banco de Dados
Sistema Financeiro - Loja Jerônimo Rosado 1994
"""
import sqlite3
import pandas as pd
from datetime import datetime, date

# ==========================================
# CONFIGURAÇÃO DO BANCO DE DADOS
# ==========================================
DB_PATH = r'C:\Users\Rodrigo  Garcia\Desktop\Maconaria\financas_loja.db'

# ==========================================
# FUNÇÕES DO BANCO DE DADOS
# ==========================================

def init_db():
    """Inicializa o banco de dados com todas as tabelas necessárias"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabela de Obreiros
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS obreiros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cim TEXT DEFAULT '000000',
            grau TEXT NOT NULL,
            valor_mensalidade REAL NOT NULL,
            isento INTEGER DEFAULT 0,
            data_admissao TEXT DEFAULT '2026-01-01',
            data_nascimento TEXT,
            email TEXT,
            telefone TEXT
        )
    """)
    
    # Adicionar colunas que podem não existir em tabelas antigas
    try:
        cursor.execute("ALTER TABLE obreiros ADD COLUMN data_nascimento TEXT")
    except sqlite3.OperationalError:
        pass  # A coluna já existe
    
    try:
        cursor.execute("ALTER TABLE obreiros ADD COLUMN email TEXT")
    except sqlite3.OperationalError:
        pass  # A coluna já existe
    
    try:
        cursor.execute("ALTER TABLE obreiros ADD COLUMN telefone TEXT")
    except sqlite3.OperationalError:
        pass  # A coluna já existe
    
    # Tabela de Categorias
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE
        )
    """)
    
    # Tabela de Transações
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            tipo TEXT NOT NULL,
            categoria TEXT NOT NULL,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            obreiro_id INTEGER,
            mes_competencia TEXT,
            ano_competencia TEXT,
            tipo_caixa TEXT DEFAULT 'Bancário',
            FOREIGN KEY (obreiro_id) REFERENCES obreiros(id) ON DELETE SET NULL
        )
    """)
    
    # Adicionar coluna tipo_caixa se não existir
    try:
        cursor.execute("ALTER TABLE transacoes ADD COLUMN tipo_caixa TEXT DEFAULT 'Bancário'")
    except sqlite3.OperationalError:
        pass  # A coluna já existe
    
    # Tabela de Notícias
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS noticias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            conteudo TEXT NOT NULL,
            data_publicacao TEXT NOT NULL,
            autor TEXT,
            ativo INTEGER DEFAULT 1
        )
    """)
    
    # Tabela de Eventos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descricao TEXT,
            data_evento TEXT NOT NULL,
            hora TEXT,
            local TEXT,
            tipo TEXT DEFAULT 'Geral'
        )
    """)
    
    # Tabela de Usuários
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            nivel_acesso TEXT DEFAULT 'usuario',
            ativo INTEGER DEFAULT 1,
            data_cadastro TEXT NOT NULL
        )
    """)
    
    # Tabela de Fila Sicredi
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fila_sicredi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_sicredi TEXT UNIQUE NOT NULL,
            data TEXT NOT NULL,
            tipo TEXT NOT NULL,
            descricao_banco TEXT NOT NULL,
            valor REAL NOT NULL,
            status_conciliacao TEXT DEFAULT 'Pendente'
        )
    """)
    
    # Tabela de Agendamentos de Pagamentos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agendamentos_pagamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            valor_total REAL NOT NULL,
            numero_parcelas INTEGER NOT NULL,
            data_primeira_parcela TEXT NOT NULL,
            intervalo_dias INTEGER DEFAULT 30,
            status TEXT DEFAULT 'Pendente',
            data_criacao TEXT NOT NULL,
            observacoes TEXT
        )
    """)
    
    # Tabela de Parcelas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parcelas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agendamento_id INTEGER NOT NULL,
            numero_parcela INTEGER NOT NULL,
            valor_parcela REAL NOT NULL,
            data_vencimento TEXT NOT NULL,
            status TEXT DEFAULT 'Pendente',
            data_pagamento TEXT,
            FOREIGN KEY (agendamento_id) REFERENCES agendamentos_pagamentos(id) ON DELETE CASCADE
        )
    """)
    
    # Adicionando o vínculo na tabela de transações para evitar duplicidade no Livro Caixa
    try:
        cursor.execute("ALTER TABLE transacoes ADD COLUMN id_sicredi TEXT UNIQUE")
    except sqlite3.OperationalError:
        pass  # A coluna já existe, segue o fluxo
    
    # Dados iniciais de obreiros (se tabela vazia)
    cursor.execute("SELECT COUNT(*) FROM obreiros")
    if cursor.fetchone()[0] == 0:
        query_ins = """
            INSERT INTO obreiros (nome, cim, grau, valor_mensalidade, isento, data_admissao) 
            VALUES (?, ?, ?, ?, ?, ?)
        """
        valores = [
            ("Agenilton Goncalves de Lima", "336627", "Mestre", 162.00, 0, "2026-01-01"),
            ("Raimundo Nonato", "123456", "Mestre", 100.00, 0, "2026-01-01"),
            ("Antonio da Silva", "789101", "Companheiro", 100.00, 0, "2026-01-01")
        ]
        cursor.executemany(query_ins, valores)
    
    # Dados iniciais de categorias (se tabela vazia)
    cursor.execute("SELECT COUNT(*) FROM categorias")
    if cursor.fetchone()[0] == 0:
        query_cat = """
            INSERT INTO categorias (nome) VALUES (?)
        """
        categorias = [
            "Mensalidade Loja",
            "Fraternidade Feminina",
            "Auxilio Funeral (PAF)",
            "Anuidade GOB Federal",
            "Anuidade GOB RN",
            "Taxa Extra",
            "Aluguel",
            "Água",
            "Luz",
            "Internet",
            "Material de Escritório",
            "Manutenção",
            "Eventos",
            "Doações",
            "Outros"
        ]
        cursor.executemany(query_cat, [(cat,) for cat in categorias])
        
    conn.commit()
    cursor.close()
    conn.close()

def buscar_dados(query, params=()):
    """Executa uma query SELECT e retorna os resultados como DataFrame"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(query, params)
        resultados = cursor.fetchall()
        colunas = [desc[0] for desc in cursor.description]
        cursor.close()
        conn.close()
        return pd.DataFrame(resultados, columns=colunas)
    except sqlite3.OperationalError as e:
        print(f"Erro na query: {e}")
        print(f"Query: {query}")
        return pd.DataFrame()

def executar_comando(query, params=()):
    """Executa um comando SQL (INSERT, UPDATE, DELETE)"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro ao executar comando: {str(e)}")
        return False

def formatar_moeda(valor):
    """Formata valor para exibição monetária brasileira"""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def formatar_data(data_str):
    """Formata data para exibição brasileira (suporta com e sem hora)"""
    if isinstance(data_str, str):
        try:
            # Tenta formatar com hora primeiro
            return datetime.strptime(data_str, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
        except ValueError:
            try:
                # Se falhar, tenta sem hora
                return datetime.strptime(data_str, '%Y-%m-%d').strftime('%d/%m/%Y')
            except ValueError:
                return data_str
    elif isinstance(data_str, datetime):
        return data_str.strftime('%d/%m/%Y')
    return data_str