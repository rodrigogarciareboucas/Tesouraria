# -*- coding: utf-8 -*-
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'financas_loja.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabela de obreiros
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
    
    # Tabela de categorias
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE
        )
    """)
    
    # Tabela de transações
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
            id_sicredi TEXT UNIQUE,
            FOREIGN KEY (obreiro_id) REFERENCES obreiros(id) ON DELETE SET NULL
        )
    """)
    
    # Tabela de noticias
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
    
    # Tabela de eventos
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
    
    # Tabela de usuarios
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
    
    # Tabela fila_sicredi
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
    
    # Inserir categorias padrão
    cursor.execute("SELECT COUNT(*) FROM categorias")
    if cursor.fetchone()[0] == 0:
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
        cursor.executemany("INSERT INTO categorias (nome) VALUES (?)", [(cat,) for cat in categorias])
    
    # Inserir usuário admin
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO usuarios (nome, email, senha, nivel_acesso, ativo, data_cadastro)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("Administrador", "admin", "admin", "admin", 1, datetime.now().strftime('%Y-%m-%d')))
    
    conn.commit()
    conn.close()
    print("Banco de dados inicializado com sucesso!")

if __name__ == "__main__":
    init_db()
