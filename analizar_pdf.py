# -*- coding: utf-8 -*-
import pdfplumber
import os

def analisar_pdf_completo(caminho_pdf):
    """Analisa o conteúdo completo de um PDF"""
    try:
        with pdfplumber.open(caminho_pdf) as pdf:
            print(f"\n{'='*60}")
            print(f"Arquivo: {os.path.basename(caminho_pdf)}")
            print(f"Total de páginas: {len(pdf.pages)}")
            print(f"{'='*60}\n")
            
            for i, pagina in enumerate(pdf.pages):
                texto = pagina.extract_text()
                if texto:
                    print(f"\n--- Página {i+1} ---")
                    print(texto)
                    print("\n")
                    
    except Exception as e:
        print(f"Erro ao ler {caminho_pdf}: {str(e)}")

# Analisar o primeiro arquivo
pasta = r"c:\Users\Rodrigo  Garcia\Desktop\Maconaria\Fichas dos Obreiros\ficha nova"
arquivos = os.listdir(pasta)
primeiro_pdf = [a for a in arquivos if a.endswith('.pdf')][0]
caminho = os.path.join(pasta, primeiro_pdf)

analisar_pdf_completo(caminho)
