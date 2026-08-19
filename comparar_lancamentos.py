# -*- coding: utf-8 -*-
import sqlite3
import re
from datetime import datetime

DB_PATH = r'C:\Users\Rodrigo  Garcia\Desktop\Maconaria\financas_loja.db'

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
                # Extrair mês, categoria e valor
                partes = linha.split('-')
                if len(partes) >= 2:
                    mes_categoria = partes[0].strip()
                    valor_str = partes[1].strip().replace('R$', '').replace('.', '').replace(',', '.')
                    
                    # Extrair mês e categoria
                    mes = mes_categoria.split()[0]
                    categoria = ' '.join(mes_categoria.split()[1:])
                    
                    # Converter valor
                    try:
                        valor = float(valor_str)
                        obreiro_atual['pagamentos'].append({
                            'mes': mes,
                            'categoria': categoria,
                            'valor': valor
                        })
                    except:
                        continue
        
        # Adicionar último obreiro
        if obreiro_atual:
            obreiros.append(obreiro_atual)
    
    return obreiros

def buscar_transacoes_obreiro(conn, obreiro_id):
    """Busca todas as transações de um obreiro no banco"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT data, tipo, categoria, valor, mes_competencia, ano_competencia 
        FROM transacoes 
        WHERE obreiro_id = ? AND tipo = 'Entrada'
    """, (obreiro_id,))
    return cursor.fetchall()

def comparar_lancamentos():
    """Compara lançamentos extraídos com banco e identifica faltantes"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    dados_extraidos = ler_dados_extraidos()
    lancamentos_faltantes = []
    
    # Mapeamento de meses para datas
    meses_map = {
        'Janeiro': '2026-01-15', 'Fevereiro': '2026-02-15', 'Março': '2026-03-15',
        'Abril': '2026-04-15', 'Maio': '2026-05-15', 'Junho': '2026-06-15',
        'Julho': '2026-07-15', 'Agosto': '2026-08-15', 'Setembro': '2026-09-15',
        'Outubro': '2026-10-15', 'Novembro': '2026-11-15', 'Dezembro': '2026-12-15'
    }
    
    for obreiro in dados_extraidos:
        # Buscar ID do obreiro no banco
        cursor.execute("SELECT id FROM obreiros WHERE cim = ?", (obreiro['cim'],))
        resultado = cursor.fetchone()
        
        if not resultado:
            print(f"⚠️ Obreiro não encontrado no banco: {obreiro['nome']} (CIM: {obreiro['cim']})")
            continue
        
        obreiro_id = resultado[0]
        transacoes_banco = buscar_transacoes_obreiro(conn, obreiro_id)
        
        # Criar conjunto de transações existentes para comparação
        transacoes_existentes = set()
        for trans in transacoes_banco:
            data, tipo, categoria, valor, mes_comp, ano_comp = trans
            chave = f"{data}_{categoria}_{valor}"
            transacoes_existentes.add(chave)
        
        # Verificar pagamentos faltantes
        for pag in obreiro['pagamentos']:
            data_pag = meses_map.get(pag['mes'], '2026-01-01')
            chave_pag = f"{data_pag}_{pag['categoria']}_{pag['valor']}"
            
            if chave_pag not in transacoes_existentes:
                lancamentos_faltantes.append({
                    'obreiro_id': obreiro_id,
                    'nome': obreiro['nome'],
                    'cim': obreiro['cim'],
                    'mes': pag['mes'],
                    'categoria': pag['categoria'],
                    'valor': pag['valor'],
                    'data': data_pag
                })
    
    conn.close()
    return lancamentos_faltantes

def inserir_lancamentos_faltantes(lancamentos):
    """Insere os lançamentos faltantes no banco"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Mapeamento de meses para inglês
    meses_map = {
        'Janeiro': 'January', 'Fevereiro': 'February', 'Março': 'March',
        'Abril': 'April', 'Maio': 'May', 'Junho': 'June',
        'Julho': 'July', 'Agosto': 'August', 'Setembro': 'September',
        'Outubro': 'October', 'Novembro': 'November', 'Dezembro': 'December'
    }
    
    inseridos = 0
    duplicados = 0
    
    for lanc in lancamentos:
        # Verificar se já existe antes de inserir
        cursor.execute("""
            SELECT COUNT(*) FROM transacoes 
            WHERE obreiro_id = ? AND data = ? AND categoria = ? AND valor = ? AND tipo = 'Entrada'
        """, (lanc['obreiro_id'], lanc['data'], lanc['categoria'], lanc['valor']))
        
        if cursor.fetchone()[0] == 0:
            mes_ingles = meses_map.get(lanc['mes'], lanc['mes'])
            cursor.execute("""
                INSERT INTO transacoes (data, tipo, categoria, descricao, valor, obreiro_id, mes_competencia, ano_competencia)
                VALUES (?, 'Entrada', ?, ?, ?, ?, ?, ?)
            """, (
                lanc['data'],
                lanc['categoria'],
                f'Pagamento {lanc["categoria"]} - {lanc["nome"]}',
                lanc['valor'],
                lanc['obreiro_id'],
                mes_ingles,
                '2026'
            ))
            inseridos += 1
            print(f"✓ Inserido: {lanc['nome']} - {lanc['categoria']} ({lanc['mes']}) - R$ {lanc['valor']:.2f}")
        else:
            duplicados += 1
    
    conn.commit()
    conn.close()
    
    print(f"\n=== Resumo ===")
    print(f"Lançamentos inseridos: {inseridos}")
    print(f"Lançamentos já existentes: {duplicados}")

if __name__ == "__main__":
    print("=== Comparando lançamentos ===\n")
    
    lancamentos_faltantes = comparar_lancamentos()
    
    print(f"Total de lançamentos faltantes encontrados: {len(lancamentos_faltantes)}")
    
    if lancamentos_faltantes:
        print("\n=== Lançamentos faltantes ===")
        for lanc in lancamentos_faltantes[:20]:  # Mostrar primeiros 20
            print(f"{lanc['nome']} - {lanc['categoria']} ({lanc['mes']}) - R$ {lanc['valor']:.2f}")
        
        if len(lancamentos_faltantes) > 20:
            print(f"... e mais {len(lancamentos_faltantes) - 20}")
        
        resposta = input("\nDeseja inserir os lançamentos faltantes? (s/n): ")
        if resposta.lower() == 's':
            inserir_lancamentos_faltantes(lancamentos_faltantes)
    else:
        print("✓ Todos os lançamentos já estão no banco de dados.")
