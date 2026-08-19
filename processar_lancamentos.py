# -*- coding: utf-8 -*-
import re
import mysql.connector
from datetime import datetime

# Configuração do banco de dados
DB_CONFIG = {
    'host': 'localhost',         
    'user': 'rodrigo',       
    'password': '12345', 
    'database': 'financas',
    'unix_socket': r'C:\Users\Rodrigo  Garcia\Desktop\Maconaria\mysql_data\mysql.sock',
    'charset': 'utf8mb4'         
}

def categorizar_transacao(descricao):
    """Categoriza automaticamente a transação baseada na descrição"""
    descricao_upper = descricao.upper()
    
    # Categorias baseadas em palavras-chave
    if 'NEOENERGIA' in descricao_upper or 'COSERN' in descricao_upper:
        return 'Energia'
    elif 'TCM' in descricao_upper or 'TV CABO' in descricao_upper:
        return 'Internet / Comunicação'
    elif 'MUNICIPIO' in descricao_upper or 'MOSSORÓ' in descricao_upper or 'IPTU' in descricao_upper:
        return 'IPTU / Taxas'
    elif 'GRANDE ORIENTE' in descricao_upper or 'GOB' in descricao_upper:
        return 'GOB Federal'
    elif 'SAQUE' in descricao_upper:
        return 'Saque Dinheiro'
    elif 'UNICONSTRU' in descricao_upper or 'CONSTRU' in descricao_upper:
        return 'Manutenção do Templo'
    elif 'T E T' in descricao_upper or 'EMPREEND' in descricao_upper:
        return 'Manutenção do Templo'
    else:
        return 'Outros'

def processar_linha(linha):
    """Processa uma linha do extrato e extrai dados"""
    try:
        # Padrão para extrair data, descrição e valor
        # Exemplo: PIX_DEB: 01/04/2026 PAGAMENTO PIX 07143850000198 NOBREZA CANINA PIX_DEB -138,60 2.337,45
        
        # Extrair data (formato DD/MM/YYYY)
        data_match = re.search(r'(\d{2}/\d{2}/\d{4})', linha)
        if not data_match:
            return None
        
        data = data_match.group(1)
        
        # Extrair valor (número negativo com vírgula decimal)
        valor_match = re.search(r'-(\d+[.,]\d+)', linha)
        if not valor_match:
            return None
        
        valor_str = valor_match.group(1).replace(',', '.')
        valor = float(valor_str)
        
        # Extrair descrição (remover data e valores)
        descricao = linha
        descricao = re.sub(r'\d{2}/\d{2}/\d{4}', '', descricao)
        descricao = re.sub(r'PAGAMENTO PIX \d+', '', descricao)
        descricao = re.sub(r'RECEBIMENTO PIX \d+', '', descricao)
        descricao = re.sub(r'PIX_DEB', '', descricao)
        descricao = re.sub(r'PIX_CRED', '', descricao)
        descricao = re.sub(r'SAQUE DIN AG RECIBO \w+', '', descricao)
        descricao = re.sub(r'-\d+[.,]\d+', '', descricao)
        descricao = re.sub(r'\d+[.,]\d+', '', descricao)
        descricao = descricao.strip()
        
        # Limitar descrição
        if len(descricao) > 100:
            descricao = descricao[:100]
        
        return {
            'data': data,
            'valor': valor,
            'descricao': descricao,
            'tipo': 'Saída'
        }
    except Exception as e:
        print(f"Erro ao processar linha: {linha} - {str(e)}")
        return None

def ler_arquivo_extraido():
    """Lê o arquivo com as transações extraídas"""
    transacoes = []
    
    with open(r"c:\Users\Rodrigo  Garcia\Desktop\Maconaria\transacoes_extraidas.txt", 'r', encoding='utf-8') as f:
        linhas = f.readlines()
        
        for linha in linhas:
            linha = linha.strip()
            if linha.startswith('PIX_DEB:') or linha.startswith('SAQUE:'):
                dados = processar_linha(linha)
                if dados:
                    transacoes.append(dados)
    
    return transacoes

def lancar_no_banco(transacoes):
    """Lança as transações no banco de dados"""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    lancados = 0
    erros = 0
    
    for trans in transacoes:
        try:
            # Converter data para formato MySQL
            data_mysql = datetime.strptime(trans['data'], '%d/%m/%Y').strftime('%Y-%m-%d')
            
            # Categorizar
            categoria = categorizar_transacao(trans['descricao'])
            
            # Mês e ano de competência
            mes_competencia = datetime.strptime(trans['data'], '%d/%m/%Y').strftime('%B')
            ano_competencia = datetime.strptime(trans['data'], '%d/%m/%Y').strftime('%Y')
            
            # Inserir
            query = """
                INSERT INTO transacoes (data, tipo, categoria, descricao, valor, mes_competencia, ano_competencia) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            params = (data_mysql, trans['tipo'], categoria, trans['descricao'], trans['valor'], mes_competencia, ano_competencia)
            
            cursor.execute(query, params)
            lancados += 1
            print(f"Lançado: {trans['data']} - {categoria} - R$ {trans['valor']:.2f} - {trans['descricao']}")
            
        except Exception as e:
            erros += 1
            print(f"Erro ao lançar: {trans} - {str(e)}")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\nTotal lançados: {lancados}")
    print(f"Total erros: {erros}")

def main():
    print("Processando transações dos extratos...")
    transacoes = ler_arquivo_extraido()
    print(f"Encontradas {len(transacoes)} transações para processar")
    
    print("\n=== Transações encontradas ===")
    for trans in transacoes[:5]:  # Mostrar primeiras 5
        print(f"{trans['data']} - R$ {trans['valor']:.2f} - {trans['descricao']}")
    
    print(f"\n... e mais {len(transacoes) - 5} transações")
    
    print("\nLançando no banco de dados...")
    lancar_no_banco(transacoes)
    print("Processo concluído!")

if __name__ == "__main__":
    main()
