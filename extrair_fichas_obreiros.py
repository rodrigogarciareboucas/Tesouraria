# -*- coding: utf-8 -*-
import pdfplumber
import os
import re
from datetime import datetime

def extrair_dados_ficha(caminho_pdf):
    """Extrai dados de uma ficha financeira anual de obreiro"""
    dados = {
        'nome': '',
        'cim': '',
        'grau': '',
        'situacao': '',
        'pagamentos': []
    }
    
    try:
        with pdfplumber.open(caminho_pdf) as pdf:
            # Extrair nome do obreiro (do nome do arquivo)
            nome_arquivo = os.path.basename(caminho_pdf)
            if 'Ficha Financeira Anual - ' in nome_arquivo:
                dados['nome'] = nome_arquivo.replace('Ficha Financeira Anual - ', '').replace('.pdf', '')
            elif 'Ficha Financeira Anual ' in nome_arquivo:
                dados['nome'] = nome_arquivo.replace('Ficha Financeira Anual ', '').replace('.pdf', '')
            else:
                dados['nome'] = nome_arquivo.replace('.pdf', '')
            
            # Processar página 2 onde está a tabela
            if len(pdf.pages) >= 2:
                pagina = pdf.pages[1]
                texto = pagina.extract_text() or ""
                
                # Extrair CIM
                cim_match = re.search(r'(\d{6})', texto)
                if cim_match:
                    dados['cim'] = cim_match.group(1)
                
                # Extrair situação
                situacao_match = re.search(r'REGULAR|ISENTO|ATIVO', texto, re.IGNORECASE)
                if situacao_match:
                    dados['situacao'] = situacao_match.group(0)
                
                # Extrair pagamentos por mês da tabela
                meses_abrev = ['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN', 'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ']
                meses_completos = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
                
                # Extrair linha de Mensalidade Loja
                mensalidade_match = re.search(r'Mensalidade Loja ([\d.,]+)', texto)
                if mensalidade_match:
                    valor_str = mensalidade_match.group(1).replace('.', '').replace(',', '.')
                    valor_mensalidade = float(valor_str)
                    
                    # Extrair valores por mês
                    linhas = texto.split('\n')
                    for linha in linhas:
                        if 'Mensalidade Loja' in linha:
                            # Esta linha contém os valores mensais
                            partes = linha.split()
                            for i, parte in enumerate(partes):
                                # Procurar valores numéricos após os meses
                                if re.match(r'^[\d.,]+$', parte):
                                    valor_str = parte.replace('.', '').replace(',', '.')
                                    try:
                                        valor = float(valor_str)
                                        if valor > 0 and i < len(meses_abrev):
                                            mes_idx = i - 1  # Ajustar índice
                                            if 0 <= mes_idx < len(meses_completos):
                                                dados['pagamentos'].append({
                                                    'mes': meses_completos[mes_idx],
                                                    'categoria': 'Mensalidade Loja',
                                                    'valor': valor,
                                                    'pago': True
                                                })
                                    except:
                                        pass
                            break
                
                # Extrair outras categorias (Fraternidade Feminina, PAF, GOB Federal, GOB RN)
                categorias = [
                    ('Fraternidade Feminina', 'Fraternidade Feminina'),
                    ('Auxílio Funeral (PAF)', 'Auxilio Funeral (PAF)'),
                    ('Anuidade GOB Federal', 'Anuidade GOB Federal'),
                    ('Anuidade GOB RN', 'Anuidade GOB RN')
                ]
                
                for cat_nome, cat_bd in categorias:
                    cat_match = re.search(rf'{cat_nome} ([\d.,]+)', texto)
                    if cat_match:
                        valor_str = cat_match.group(1).replace('.', '').replace(',', '.')
                        valor_cat = float(valor_str)
                        
                        # Encontrar linha desta categoria e extrair valores mensais
                        linhas = texto.split('\n')
                        for linha in linhas:
                            if cat_nome in linha:
                                partes = linha.split()
                                for i, parte in enumerate(partes):
                                    if re.match(r'^[\d.,]+$', parte):
                                        valor_str = parte.replace('.', '').replace(',', '.')
                                        try:
                                            valor = float(valor_str)
                                            if valor > 0 and i < len(meses_abrev):
                                                mes_idx = i - 1
                                                if 0 <= mes_idx < len(meses_completos):
                                                    dados['pagamentos'].append({
                                                        'mes': meses_completos[mes_idx],
                                                        'categoria': cat_bd,
                                                        'valor': valor,
                                                        'pago': True
                                                    })
                                        except:
                                            pass
                                break
                    
    except Exception as e:
        print(f"Erro ao ler {caminho_pdf}: {str(e)}")
        
    return dados

def main():
    pasta = r"c:\Users\Rodrigo  Garcia\Desktop\Maconaria\Fichas dos Obreiros\ficha nova"
    arquivos = os.listdir(pasta)
    
    print("Processando todos os arquivos...")
    todos_dados = {}
    
    for arquivo in arquivos:
        if arquivo.endswith('.pdf'):
            caminho = os.path.join(pasta, arquivo)
            print(f"Processando: {arquivo}")
            dados = extrair_dados_ficha(caminho)
            todos_dados[arquivo] = dados
            print(f"  Nome: {dados['nome']}")
            print(f"  CIM: {dados['cim']}")
            print(f"  Situação: {dados['situacao']}")
            print(f"  Pagamentos: {len(dados['pagamentos'])} lançamentos")
            print()
            
    # Salvar resultados
    with open(r"c:\Users\Rodrigo  Garcia\Desktop\Maconaria\dados_obreiros_extraidos.txt", 'w', encoding='utf-8') as f:
        for arquivo, dados in todos_dados.items():
            f.write(f"\n{'='*50}\n")
            f.write(f"Arquivo: {arquivo}\n")
            f.write(f"{'='*50}\n")
            f.write(f"Nome: {dados['nome']}\n")
            f.write(f"CIM: {dados['cim']}\n")
            f.write(f"Situação: {dados['situacao']}\n")
            f.write(f"Pagamentos:\n")
            for pag in dados['pagamentos']:
                f.write(f"  {pag['mes']} - {pag['categoria']}: R$ {pag['valor']:.2f}\n")
    
    print("\nDados extraídos e salvos em dados_obreiros_extraidos.txt")

if __name__ == "__main__":
    main()
