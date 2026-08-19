import os
import sqlite3
import requests
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime, timedelta
from dotenv import load_dotenv

# ==========================================
# CONFIGURAÇÕES DE AMBIENTE E CAMINHOS
# ==========================================
load_dotenv() # Carrega as chaves do arquivo .env

SICREDI_CLIENT_ID = os.getenv("SICREDI_CLIENT_ID")
SICREDI_CLIENT_SECRET = os.getenv("SICREDI_CLIENT_SECRET")
SICREDI_CERT_PATH = os.getenv("SICREDI_CERT_PATH") # Caminho para o certificado mTLS

# Ajuste para o diretório absoluto do seu projeto (Windows)
BASE_DIR = r"C:\Users\Rodrigo  Garcia\Desktop\Maconaria"
DB_PATH = os.path.join(BASE_DIR, "financas_loja.db")
LOG_DIR = os.path.join(BASE_DIR, "logs")

# ==========================================
# SISTEMA DE LOGS (Rotativo)
# ==========================================
os.makedirs(LOG_DIR, exist_ok=True)
log_file = os.path.join(LOG_DIR, "sync_sicredi.log")

# Rotaciona o log todo dia à meia-noite e mantém o histórico dos últimos 30 dias
handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=30)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

logger = logging.getLogger("SicrediSync")
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# ==========================================
# FUNÇÕES DE INTEGRAÇÃO
# ==========================================
def obter_token():
    """Autentica na API do Sicredi usando mTLS e retorna o Token de Acesso."""
    url = "https://api-ssl.sicredi.com.br/v1/oauth/token" # URL de exemplo, confirme na documentação atual
    payload = {"grant_type": "client_credentials"}
    
    try:
        # A requisição exige a passagem do certificado digital
        resposta = requests.post(
            url, 
            data=payload, 
            auth=(SICREDI_CLIENT_ID, SICREDI_CLIENT_SECRET),
            cert=SICREDI_CERT_PATH
        )
        resposta.raise_for_status()
        logger.info("Token de acesso obtido com sucesso.")
        return resposta.json().get("access_token")
    except Exception as e:
        logger.error(f"Erro ao obter token do Sicredi: {e}")
        return None

def buscar_extrato(token):
    """Busca os lançamentos (entradas e saídas) dos últimos dias."""
    # Defina a janela de busca (ex: últimos 3 dias para garantir que nada foi perdido)
    data_inicio = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
    data_fim = datetime.now().strftime("%Y-%m-%d")
    
    url = f"https://api-ssl.sicredi.com.br/v1/contas/extrato?dataInicio={data_inicio}&dataFim={data_fim}"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        resposta = requests.get(url, headers=headers, cert=SICREDI_CERT_PATH)
        resposta.raise_for_status()
        logger.info(f"Extrato buscado com sucesso: {data_inicio} a {data_fim}")
        return resposta.json().get("lancamentos", [])
    except Exception as e:
        logger.error(f"Erro ao buscar extrato: {e}")
        return []

def salvar_na_fila(lancamentos):
    """Salva lançamentos na fila do SQLite, ignorando duplicidades de forma silenciosa."""
    if not lancamentos:
        logger.info("Nenhum lançamento novo para processar.")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        inseridos = 0
        
        for lanc in lancamentos:
            # O OR IGNORE instrui o SQLite a simplesmente pular a linha se o id_sicredi já existir
            # Isso é o coração do nosso bloqueio de duplicidade (idempotência)
            cursor.execute("""
                INSERT OR IGNORE INTO fila_sicredi 
                (id_sicredi, data, tipo, descricao_banco, valor, status_conciliacao) 
                VALUES (?, ?, ?, ?, ?, 'Pendente')
            """, (
                lanc['idTransacao'], # Ajuste os nomes das chaves conforme o JSON real da API do Sicredi
                lanc['dataLancamento'],
                "Entrada" if lanc['valor'] > 0 else "Saída",
                lanc['descricao'],
                abs(lanc['valor']) # Salvamos o valor absoluto, o "Tipo" define se é receita ou despesa
            ))
            
            # Se rowcount > 0, significa que a restrição UNIQUE não barrou, logo, era um registro inédito
            if cursor.rowcount > 0:
                inseridos += 1
                
        conn.commit()
        logger.info(f"Sincronização concluída: {inseridos} novos registros inseridos na fila.")
        
    except sqlite3.Error as e:
        logger.error(f"Erro de banco de dados ao salvar na fila: {e}")
    finally:
        if conn:
            conn.close()

# ==========================================
# EXECUÇÃO PRINCIPAL
# ==========================================
if __name__ == "__main__":
    logger.info("Iniciando rotina de sincronização bancária...")
    
    token = obter_token()
    if token:
        lancamentos = buscar_extrato(token)
        salvar_na_fila(lancamentos)
    else:
        logger.warning("Sincronização abortada devido a falha na autenticação.")