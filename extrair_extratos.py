# -*- coding: utf-8 -*-
import PyPDF2
import os
import re
from datetime import datetime

def extrair_dados_pdf(caminho_pdf):
    """Extrai dados de um PDF de extrato bancário"""
    dados = []
    try:
        with open(caminho_pdf, 'rb') as arquivo:
            leitor = PyPDF2.PdfReader(arquivo)
            texto_completo = ""
            for pagina in leitor.pages:
                texto_completo += pagina.extract_text()
            
            # Procurar por padrões de PIX_DEB e saques
            linhas = texto_completo.split('\n')
            
            for linha in linhas:
                # Procurar por PIX_DEB
                if 'PIX_DEB' in linha or 'PIX DEB' in linha:
                    dados.append({
                        'tipo': 'PIX_DEB',
                        'linha': linha.strip()
                    })
                # Procurar por saques
                elif 'SAQUE' in linha or 'Saque' in linha:
                    dados.append({
                        'tipo': 'SAQUE',
                        'linha': linha.strip()
                    })
                    
    except Exception as e:
        print(f"Erro ao ler {caminho_pdf}: {str(e)}")
        
    return dados

def main():
    pasta = r"c:\Users\Rodrigo  Garcia\Desktop\Maconaria\extrato sicredi"
    arquivos = os.listdir(pasta)
    
    todos_dados = {}
    
    for arquivo in arquivos:
        if arquivo.endswith('.pdf'):
            caminho = os.path.join(pasta, arquivo)
            print(f"Processando: {arquivo}")
            dados = extrair_dados_pdf(caminho)
            todos_dados[arquivo] = dados
            print(f"  Encontrados: {len(dados)} transações")
            
    # Salvar resultados
    with open(r"c:\Users\Rodrigo  Garcia\Desktop\Maconaria\transacoes_extraidas.txt", 'w', encoding='utf-8') as f:
        for arquivo, dados in todos_dados.items():
            f.write(f"\n{'='*50}\n")
            f.write(f"Arquivo: {arquivo}\n")
            f.write(f"{'='*50}\n")
            for item in dados:
                f.write(f"{item['tipo']}: {item['linha']}\n")
    
    print("\nDados extraídos e salvos em transacoes_extraidas.txt")

if __name__ == "__main__":
    main()
