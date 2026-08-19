# -*- coding: utf-8 -*-
import os
import PyPDF2
import re
from datetime import datetime

PASTA_FICHAS = r'c:\Users\Rodrigo  Garcia\Desktop\Maconaria\Fichas dos Obreiros\ficha nova'

def extrair_dados_ficha(caminho_pdf):
    """Extrai dados de uma ficha financeira PDF"""
    dados = {
        'nome': '',
        'cim': '',
        'situacao': '',
        'pagamentos': []
    }
    
    try:
        with open(caminho_pdf, 'rb') as arquivo:
            leitor = PyPDF2.PdfReader(arquivo)
            texto_completo = ''
            
            for pagina in leitor.pages:
                texto_completo += pagina.extract_text()
            
            # Extrair nome
            nome_match = re.search(r'Nome:\s*(.+)', texto_completo)
            if nome_match:
                dados['nome'] = nome_match.group(1).strip()
            
            # Extrair CIM
            cim_match = re.search(r'CIM:\s*(\d+)', texto_completo)
            if cim_match:
                dados['cim'] = cim_match.group(1).strip()
            
            # Extrair situação
            situacao_match = re.search(r'Situação:\s*(.+)', texto_completo)
            if situacao_match:
                dados['situacao'] = situacao_match.group(1).strip()
            
            # Extrair pagamentos
            padrao_pagamento = r'(\w+)\s*-\s*([^:]+):\s*R\$\s*([\d.,]+)'
            pagamentos = re.findall(padrao_pagamento, texto_completo)
            
            for mes, categoria, valor in pagamentos:
                valor_limpo = valor.replace('.', '').replace(',', '.')
                try:
                    dados['pagamentos'].append({
                        'mes': mes.strip(),
                        'categoria': categoria.strip(),
                        'valor': float(valor_limpo)
                    })
                except:
                    pass
    
    except Exception as e:
        print(f"Erro ao ler {caminho_pdf}: {e}")
    
    return dados

def analisar_fichas():
    """Analisa todas as fichas na pasta"""
    fichas = []
    
    for arquivo in os.listdir(PASTA_FICHAS):
        if arquivo.endswith('.pdf'):
            caminho = os.path.join(PASTA_FICHAS, arquivo)
            dados = extrair_dados_ficha(caminho)
            if dados['nome']:
                fichas.append(dados)
                print(f"\n=== {arquivo} ===")
                print(f"Nome: {dados['nome']}")
                print(f"CIM: {dados['cim']}")
                print(f"Situação: {dados['situacao']}")
                print(f"Total de pagamentos: {len(dados['pagamentos'])}")
                
                # Resumo por categoria
                categorias = {}
                for pag in dados['pagamentos']:
                    cat = pag['categoria']
                    if cat not in categorias:
                        categorias[cat] = []
                    categorias[cat].append(pag)
                
                for cat, pags in categorias.items():
                    print(f"  {cat}: {len(pags)} pagamentos")
                    for p in pags[:3]:  # Mostrar primeiros 3
                        print(f"    - {p['mes']}: R$ {p['valor']:.2f}")
                    if len(pags) > 3:
                        print(f"    ... e mais {len(pags) - 3}")
    
    return fichas

if __name__ == "__main__":
    print("=== Analisando fichas financeiras ===")
    fichas = analisar_fichas()
    print(f"\n=== Total de fichas analisadas: {len(fichas)} ===")
