# -*- coding: utf-8 -*-
import mysql.connector
import pandas as pd

# Configuração do banco de dados
DB_CONFIG = {
    'host': 'localhost',         
    'user': 'rodrigo',       
    'password': '12345', 
    'database': 'financas',
    'unix_socket': r'C:\Users\Rodrigo  Garcia\Desktop\Maconaria\mysql_data\mysql.sock',
    'charset': 'utf8mb4'         
}

def verificar_lancamentos():
    """Verifica os lançamentos realizados"""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    
    # Contar total de transações
    cursor.execute("SELECT COUNT(*) as total FROM transacoes")
    total = cursor.fetchone()['total']
    print(f"Total de transações no banco: {total}")
    
    # Contar por tipo
    cursor.execute("SELECT tipo, COUNT(*) as count FROM transacoes GROUP BY tipo")
    tipos = cursor.fetchall()
    print("\nTransações por tipo:")
    for t in tipos:
        print(f"  {t['tipo']}: {t['count']}")
    
    # Contar por categoria
    cursor.execute("SELECT categoria, COUNT(*) as count, SUM(valor) as total_valor FROM transacoes GROUP BY categoria ORDER BY count DESC")
    categorias = cursor.fetchall()
    print("\nTransações por categoria:")
    for c in categorias:
        print(f"  {c['categoria']}: {c['count']} lançamentos - Total: R$ {c['total_valor']:.2f}")
    
    # Mostrar últimas 10 transações
    cursor.execute("SELECT * FROM transacoes ORDER BY id DESC LIMIT 10")
    ultimas = cursor.fetchall()
    print("\nÚltimas 10 transações:")
    for u in ultimas:
        print(f"  {u['data']} - {u['tipo']} - {u['categoria']} - R$ {u['valor']:.2f} - {u['descricao']}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    verificar_lancamentos()
