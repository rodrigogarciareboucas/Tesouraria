# -*- coding: utf-8 -*-
import os
import sys
import subprocess
from init_db import init_db

def main():
    # Inicializar banco de dados
    print("Inicializando banco de dados...")
    init_db()
    
    # Executar o Streamlit
    script_dir = os.path.dirname(os.path.abspath(__file__))
    financeiro_path = os.path.join(script_dir, 'financeiro.py')
    
    print("Iniciando o Sistema Financeiro...")
    subprocess.run([sys.executable, '-m', 'streamlit', 'run', financeiro_path])

if __name__ == "__main__":
    main()
