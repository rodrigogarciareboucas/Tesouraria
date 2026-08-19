# -*- coding: utf-8 -*-
import mysql.connector

# Configuração do banco de dados
DB_CONFIG = {
    'host': 'localhost',         
    'user': 'rodrigo',       
    'password': '12345', 
    'database': 'financas',
    'unix_socket': r'C:\Users\Rodrigo  Garcia\Desktop\Maconaria\mysql_data\mysql.sock',
    'charset': 'utf8mb4'         
}

def limpar_pagamentos_obreiros():
    """Remove os pagamentos de obreiros que foram lançados com valores incorretos"""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Remover transações de obreiros (tipo Entrada e obreiro_id não nulo)
        query = "DELETE FROM transacoes WHERE tipo = 'Entrada' AND obreiro_id IS NOT NULL"
        cursor.execute(query)
        
        removidos = cursor.rowcount
        conn.commit()
        
        print(f"Removidos {removidos} lançamentos de obreiros com valores incorretos")
        
    except Exception as e:
        print(f"Erro ao limpar pagamentos: {str(e)}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    limpar_pagamentos_obreiros()
