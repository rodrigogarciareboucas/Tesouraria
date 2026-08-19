# -*- coding: utf-8 -*-
import PyInstaller.__main__
import os

def build_exe():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    PyInstaller.__main__.run([
        'launcher.py',
        '--name=SistemaFinanceiro',
        '--onefile',
        '--windowed',
        '--icon=logo.png' if os.path.exists('logo.png') else '',
        '--add-data=financeiro.py;.',
        '--add-data=init_db.py;.',
        '--add-data=logo.png;.' if os.path.exists('logo.png') else '',
        '--hidden-import=streamlit',
        '--hidden-import=pandas',
        '--hidden-import=plotly',
        '--hidden-import=fpdf',
        '--hidden-import=sqlite3',
        '--clean',
        '--noconfirm'
    ])

if __name__ == "__main__":
    print("Iniciando build do executável...")
    build_exe()
    print("Build concluído! O executável está na pasta dist/")
