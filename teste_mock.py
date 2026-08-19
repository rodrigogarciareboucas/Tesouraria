import sqlite3
import os
from datetime import datetime

# Ajuste o caminho do banco de dados para o seu ambiente local
BASE_DIR = r"C:\Users\Rodrigo  Garcia\Desktop\Maconaria"
DB_PATH = os.path.join(BASE_DIR, "financas_loja.db")

def simular_resposta_api():
    """Retorna um JSON estático simulando o payload da API do Sicredi."""
    hoje = datetime.now().strftime("%Y-%m-%d")
    
    return [
        {
            "idTransacao": "SICREDI-PIX-001",
            "dataLancamento": hoje,
            "descricao": "PIX RECEBIDO - ANTONIO DA SILVA",
            "valor": 162.00
        },
        {
            "idTransacao": "SICREDI-PAG-002",
            "dataLancamento": hoje,
            "descricao": "PAG BOLETO - COSERN (ENERGIA)",
            "valor": -245.50
        },
        {
            "idTransacao": "SICREDI-TRANSF-003",
            "dataLancamento": hoje,
            "descricao": "TED RECEBIDA - DOACAO EVENTO",
            "valor": 500.00
        }
    ]

def salvar_na_fila(lancamentos):
    """Salva os lançamentos simulados na tabela fila_sicredi."""
    print("Conectando ao banco de dados...")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        inseridos = 0
        
        for lanc in lancamentos:
            # Identifica se é Entrada ou Saída com base no sinal do valor
            tipo = "Entrada" if lanc['valor'] > 0 else "Saída"
            valor_absoluto = abs(lanc['valor'])
            
            cursor.execute("""
                INSERT OR IGNORE INTO fila_sicredi 
                (id_sicredi, data, tipo, descricao_banco, valor, status_conciliacao) 
                VALUES (?, ?, ?, ?, ?, 'Pendente')
            """, (
                lanc['idTransacao'],
                lanc['dataLancamento'],
                tipo,
                lanc['descricao'],
                valor_absoluto
            ))
            
            if cursor.rowcount > 0:
                inseridos += 1
                
        conn.commit()
        print(f"Sucesso! {inseridos} novos registros inseridos na fila de conciliação.")
        
    except sqlite3.Error as e:
        print(f"Erro no banco de dados: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("Iniciando simulação da API do Sicredi...")
    dados_falsos = simular_resposta_api()
    salvar_na_fila(dados_falsos)
    print("Simulação concluída. Abra o seu painel do Streamlit!")
