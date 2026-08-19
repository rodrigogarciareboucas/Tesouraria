# -*- coding: utf-8 -*-
import mysql.connector
import re
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

def ler_dados_extraidos():
    """Lê os dados extraídos do arquivo txt"""
    obreiros = []
    
    with open(r"c:\Users\Rodrigo  Garcia\Desktop\Maconaria\dados_obreiros_extraidos.txt", 'r', encoding='utf-8') as f:
        linhas = f.readlines()
        
        obreiro_atual = None
        dentro_pagamentos = False
        
        for linha in linhas:
            linha_original = linha
            linha = linha.strip()
            
            # Detectar início de novo obreiro
            if linha.startswith('Arquivo:'):
                if obreiro_atual:
                    obreiros.append(obreiro_atual)
                obreiro_atual = {
                    'arquivo': linha.replace('Arquivo: ', ''),
                    'nome': '',
                    'cim': '',
                    'situacao': '',
                    'pagamentos': []
                }
                dentro_pagamentos = False
            elif 'Nome:' in linha and obreiro_atual:
                obreiro_atual['nome'] = linha.replace('Nome: ', '')
            elif 'CIM:' in linha and obreiro_atual:
                obreiro_atual['cim'] = linha.replace('CIM: ', '')
            elif 'Situação:' in linha and obreiro_atual:
                obreiro_atual['situacao'] = linha.replace('Situação: ', '')
            elif 'Pagamentos:' in linha and obreiro_atual:
                dentro_pagamentos = True
            elif dentro_pagamentos and '-' in linha and ':' in linha and obreiro_atual:
                # Linha de pagamento: "  Fevereiro - Mensalidade Loja: R$ 162.00"
                partes = linha.split('-')
                if len(partes) >= 2:
                    mes = partes[0].strip()
                    resto = partes[1].strip()
                    
                    # Extrair categoria e valor
                    cat_valor = resto.split(':')
                    if len(cat_valor) >= 2:
                        categoria = cat_valor[0].strip()
                        valor_str = cat_valor[1].strip().replace('R$', '').strip()
                        # Converter formato brasileiro (162.00) para formato float (162.00)
                        # No formato brasileiro, ponto é separador de milhar e vírgula é decimal
                        # Mas no arquivo os valores estão como "162.00" (ponto como decimal)
                        try:
                            valor = float(valor_str)
                            obreiro_atual['pagamentos'].append({
                                'mes': mes,
                                'categoria': categoria,
                                'valor': valor
                            })
                        except:
                            pass
            elif dentro_pagamentos and linha.startswith('==='):
                dentro_pagamentos = False
        
        # Adicionar último obreiro
        if obreiro_atual:
            obreiros.append(obreiro_atual)
    
    return obreiros

def cadastrar_obreiro(obreiro):
    """Cadastra um obreiro no sistema"""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Verificar se obreiro já existe pelo CIM
        cursor.execute("SELECT id FROM obreiros WHERE cim = %s", (obreiro['cim'],))
        existente = cursor.fetchone()
        
        if existente:
            print(f"Obreiro {obreiro['nome']} (CIM: {obreiro['cim']}) já cadastrado. ID: {existente[0]}")
            return existente[0]
        
        # Determinar valor da mensalidade baseado nos pagamentos
        valor_mensalidade = 0.0
        for pag in obreiro['pagamentos']:
            if 'Mensalidade Loja' in pag['categoria']:
                valor_mensalidade = pag['valor']
                break
        
        # Determinar se é isento
        isento = 1 if obreiro['situacao'].upper() == 'ISENTO' else 0
        
        # Inserir obreiro
        query = """
            INSERT INTO obreiros (nome, cim, grau, valor_mensalidade, isento, data_admissao) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (obreiro['nome'], obreiro['cim'], 'Mestre', valor_mensalidade, isento, '2026-01-01')
        
        cursor.execute(query, params)
        conn.commit()
        
        obreiro_id = cursor.lastrowid
        print(f"Obreiro {obreiro['nome']} cadastrado com sucesso. ID: {obreiro_id}")
        
        return obreiro_id
        
    except Exception as e:
        print(f"Erro ao cadastrar obreiro {obreiro['nome']}: {str(e)}")
        return None
    finally:
        cursor.close()
        conn.close()

def mapear_mes_para_data(mes, ano='2026'):
    """Mapeia nome do mês para data"""
    meses = {
        'Janeiro': '01',
        'Fevereiro': '02',
        'Março': '03',
        'Abril': '04',
        'Maio': '05',
        'Junho': '06',
        'Julho': '07',
        'Agosto': '08',
        'Setembro': '09',
        'Outubro': '10',
        'Novembro': '11',
        'Dezembro': '12'
    }
    
    mes_num = meses.get(mes, '01')
    return f"{ano}-{mes_num}-15"  # Dia 15 do mês

def lancar_pagamentos(obreiro, obreiro_id):
    """Lança os pagamentos de um obreiro no sistema"""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    lancados = 0
    
    try:
        print(f"  Processando {len(obreiro['pagamentos'])} pagamentos...")
        
        for pag in obreiro['pagamentos']:
            # Mapear categoria do PDF para categoria do sistema
            categoria_map = {
                'Mensalidade Loja': 'Mensalidade Loja',
                'Fraternidade Feminina': 'Fraternidade Feminina',
                'Auxilio Funeral (PAF)': 'Auxilio Funeral (PAF)',
                'Anuidade GOB Federal': 'Anuidade GOB Federal',
                'Anuidade GOB RN': 'Anuidade GOB RN'
            }
            
            categoria_sistema = categoria_map.get(pag['categoria'], pag['categoria'])
            
            # Converter mês para data
            data_pagamento = mapear_mes_para_data(pag['mes'])
            
            # Verificar se pagamento já existe
            query_check = """
                SELECT id FROM transacoes 
                WHERE obreiro_id = %s AND categoria = %s AND mes_competencia = %s
            """
            mes_competencia = pag['mes']
            cursor.execute(query_check, (obreiro_id, categoria_sistema, mes_competencia))
            existente = cursor.fetchone()
            
            if existente:
                print(f"  Pagamento já existe: {pag['mes']} - {categoria_sistema}")
                continue
            
            # Inserir pagamento
            query = """
                INSERT INTO transacoes (data, tipo, categoria, descricao, valor, obreiro_id, mes_competencia, ano_competencia) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            descricao = f"{pag['categoria']} - {obreiro['nome']}"
            params = (data_pagamento, 'Entrada', categoria_sistema, descricao, pag['valor'], obreiro_id, mes_competencia, '2026')
            
            cursor.execute(query, params)
            lancados += 1
            print(f"  Lançado: {pag['mes']} - {categoria_sistema} - R$ {pag['valor']:.2f}")
        
        conn.commit()
        
    except Exception as e:
        print(f"Erro ao lançar pagamentos: {str(e)}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
    
    return lancados

def main():
    print("Lendo dados extraídos...")
    obreiros = ler_dados_extraidos()
    print(f"Encontrados {len(obreiros)} obreiros para processar\n")
    
    total_cadastrados = 0
    total_lancamentos = 0
    
    for obreiro in obreiros:
        print(f"\nProcessando: {obreiro['nome']}")
        
        # Cadastrar obreiro
        obreiro_id = cadastrar_obreiro(obreiro)
        
        if obreiro_id:
            total_cadastrados += 1
            
            # Lançar pagamentos
            lancamentos = lancar_pagamentos(obreiro, obreiro_id)
            total_lancamentos += lancamentos
    
    print(f"\n{'='*50}")
    print(f"RESUMO:")
    print(f"Obreiros cadastrados: {total_cadastrados}")
    print(f"Pagamentos lançados: {total_lancamentos}")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
