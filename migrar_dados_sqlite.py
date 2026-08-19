# -*- coding: utf-8 -*-
import sqlite3
import re
from datetime import datetime

DB_PATH = r'C:\Users\Rodrigo  Garcia\Desktop\Maconaria\financas_loja.db'

def migrar_obreiros():
    """Migra dados de obreiros do arquivo txt para SQLite"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    with open(r"c:\Users\Rodrigo  Garcia\Desktop\Maconaria\dados_obreiros_extraidos.txt", 'r', encoding='utf-8') as f:
        linhas = f.readlines()
        
        obreiro_atual = None
        dentro_pagamentos = False
        
        for linha in linhas:
            linha = linha.strip()
            
            if linha.startswith('Arquivo:'):
                if obreiro_atual:
                    # Inserir obreiro no SQLite
                    cursor.execute("""
                        INSERT OR REPLACE INTO obreiros (nome, cim, grau, valor_mensalidade, isento, data_admissao)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        obreiro_atual['nome'],
                        obreiro_atual['cim'],
                        obreiro_atual.get('grau', 'Mestre'),
                        obreiro_atual.get('valor_mensalidade', 162.00),
                        0,
                        '2026-01-01'
                    ))
                    print(f"  ✓ Obreiro inserido: {obreiro_atual['nome']}")
                
                obreiro_atual = {'nome': '', 'cim': '', 'grau': 'Mestre', 'valor_mensalidade': 162.00}
                dentro_pagamentos = False
            elif 'Nome:' in linha and obreiro_atual:
                obreiro_atual['nome'] = linha.replace('Nome: ', '')
            elif 'CIM:' in linha and obreiro_atual:
                obreiro_atual['cim'] = linha.replace('CIM: ', '')
        
        # Inserir último obreiro
        if obreiro_atual:
            cursor.execute("""
                INSERT OR REPLACE INTO obreiros (nome, cim, grau, valor_mensalidade, isento, data_admissao)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                obreiro_atual['nome'],
                obreiro_atual['cim'],
                obreiro_atual.get('grau', 'Mestre'),
                obreiro_atual.get('valor_mensalidade', 162.00),
                0,
                '2026-01-01'
            ))
            print(f"  ✓ Obreiro inserido: {obreiro_atual['nome']}")
    
    conn.commit()
    conn.close()
    print("✓ Migração de obreiros concluída")

def migrar_transacoes():
    """Migra dados de transações do arquivo txt para SQLite"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Mapeamento de categorias
    categoria_map = {
        'NEOENERGIA': 'Luz',
        'COSERN': 'Luz',
        'CAERN': 'Água',
        'TCM': 'Internet',
        'TV CABO': 'Internet',
        'GRANDE ORIENTE': 'Anuidade GOB Federal',
        'GOB': 'Anuidade GOB Federal',
        'UNICONSTRU': 'Manutenção',
        'CONSTRU': 'Manutenção',
        'T E T': 'Manutenção',
        'EMPREEND': 'Manutenção',
        'MUNICIPIO': 'Aluguel',
        'MOSSORÓ': 'Aluguel',
        'IPTU': 'Aluguel'
    }
    
    with open(r"c:\Users\Rodrigo  Garcia\Desktop\Maconaria\transacoes_extraidas.txt", 'r', encoding='utf-8') as f:
        linhas = f.readlines()
        
        for linha in linhas:
            linha = linha.strip()
            
            # Padrão para extrair data, descrição e valor
            data_match = re.search(r'(\d{2}/\d{2}/\d{4})', linha)
            if not data_match:
                continue
            
            data_str = data_match.group(1)
            data_obj = datetime.strptime(data_str, '%d/%m/%Y')
            data_formatada = data_obj.strftime('%Y-%m-%d')
            
            # Extrair valor (último número negativo na linha)
            valor_match = re.search(r'-([\d.,]+)$', linha)
            if valor_match:
                valor_str = valor_match.group(1).replace('.', '').replace(',', '.')
                valor = float(valor_str) * -1  # Converter para positivo
                
                # Extrair descrição
                descricao = linha.split(data_str)[1].strip()
                
                # Categorizar
                categoria = 'Outros'
                for key, cat in categoria_map.items():
                    if key in descricao.upper():
                        categoria = cat
                        break
                
                # Inserir transação
                cursor.execute("""
                    INSERT INTO transacoes (data, tipo, categoria, descricao, valor, mes_competencia, ano_competencia)
                    VALUES (?, 'Saída', ?, ?, ?, ?, ?)
                """, (
                    data_formatada,
                    categoria,
                    descricao[:200],
                    valor,
                    data_obj.strftime('%B'),
                    str(data_obj.year)
                ))
                print(f"  ✓ Transação inserida: {data_formatada} - {categoria} - R$ {valor:.2f}")
    
    conn.commit()
    conn.close()
    print("✓ Migração de transações concluída")

def migrar_pagamentos_obreiros():
    """Migra pagamentos de obreiros do arquivo txt para SQLite"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Mapeamento de meses
    meses_map = {
        'Janeiro': 'January', 'Fevereiro': 'February', 'Março': 'March',
        'Abril': 'April', 'Maio': 'May', 'Junho': 'June',
        'Julho': 'July', 'Agosto': 'August', 'Setembro': 'September',
        'Outubro': 'October', 'Novembro': 'November', 'Dezembro': 'December'
    }
    
    # Mapeamento de datas por mês
    datas_por_mes = {
        'January': '2026-01-15', 'February': '2026-02-15', 'March': '2026-03-15',
        'April': '2026-04-15', 'May': '2026-05-15', 'June': '2026-06-15',
        'July': '2026-07-15', 'August': '2026-08-15', 'September': '2026-09-15',
        'October': '2026-10-15', 'November': '2026-11-15', 'December': '2026-12-15'
    }
    
    with open(r"c:\Users\Rodrigo  Garcia\Desktop\Maconaria\dados_obreiros_extraidos.txt", 'r', encoding='utf-8') as f:
        linhas = f.readlines()
        
        obreiro_atual = None
        dentro_pagamentos = False
        
        for linha in linhas:
            linha = linha.strip()
            
            if linha.startswith('Arquivo:'):
                obreiro_atual = {'nome': '', 'cim': ''}
                dentro_pagamentos = False
            elif 'Nome:' in linha and obreiro_atual:
                obreiro_atual['nome'] = linha.replace('Nome: ', '')
            elif 'CIM:' in linha and obreiro_atual:
                obreiro_atual['cim'] = linha.replace('CIM: ', '')
            elif 'Pagamentos:' in linha:
                dentro_pagamentos = True
            elif dentro_pagamentos and linha and not linha.startswith('===') and not linha.startswith('Situação'):
                # Padrão: "Fevereiro - Mensalidade Loja: R$ 162.00"
                if ' - ' in linha and ':' in linha and 'R$' in linha:
                    try:
                        # Extrair mês e categoria
                        partes = linha.split(' - ')
                        mes = partes[0].strip()
                        resto = partes[1].strip()
                        
                        separador_valor = resto.find(':')
                        categoria = resto[:separador_valor].strip()
                        valor_str = resto[separador_valor+1:].strip().replace('R$', '').strip()
                        
                        # Converter valor corretamente
                        # Se tem vírgula, é formato brasileiro (1.234,56) -> remover ponto, trocar vírgula por ponto
                        # Se só tem ponto, é formato internacional (162.00) -> não remover ponto
                        if ',' in valor_str:
                            valor_str = valor_str.replace('.', '').replace(',', '.')
                        valor = float(valor_str)
                        
                        # Buscar ID do obreiro
                        cursor.execute("SELECT id FROM obreiros WHERE cim = ?", (obreiro_atual['cim'],))
                        obreiro_id = cursor.fetchone()
                        
                        if obreiro_id:
                            obreiro_id = obreiro_id[0]
                            mes_ingles = meses_map.get(mes, mes)
                            data_pagamento = datas_por_mes.get(mes_ingles, '2026-01-01')
                            
                            # Inserir pagamento
                            cursor.execute("""
                                INSERT INTO transacoes (data, tipo, categoria, descricao, valor, obreiro_id, mes_competencia, ano_competencia)
                                VALUES (?, 'Entrada', ?, ?, ?, ?, ?, ?)
                            """, (
                                data_pagamento,
                                categoria,
                                f'Pagamento {categoria} - {obreiro_atual["nome"]}',
                                valor,
                                obreiro_id,
                                mes_ingles,
                                '2026'
                            ))
                            print(f"  ✓ Pagamento inserido: {obreiro_atual['nome']} - {categoria} - R$ {valor:.2f}")
                    except Exception as e:
                        print(f"  ✗ Erro ao processar linha: {linha[:50]}... - {e}")
                        continue
    
    conn.commit()
    conn.close()
    print("✓ Migração de pagamentos concluída")

def adicionar_categorias():
    """Adiciona categorias padrão ao SQLite"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
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
    
    for cat in categorias:
        cursor.execute("INSERT OR IGNORE INTO categorias (nome) VALUES (?)", (cat,))
        print(f"  ✓ Categoria inserida: {cat}")
    
    conn.commit()
    conn.close()
    print("✓ Categorias adicionadas")

if __name__ == "__main__":
    print("=== Iniciando migração de dados para SQLite ===\n")
    
    print("1. Adicionando categorias...")
    adicionar_categorias()
    
    print("\n2. Migrando obreiros...")
    migrar_obreiros()
    
    print("\n3. Migrando pagamentos de obreiros...")
    migrar_pagamentos_obreiros()
    
    print("\n4. Migrando transações...")
    migrar_transacoes()
    
    print("\n=== Migração concluída ===")
