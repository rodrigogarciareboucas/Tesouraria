# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA E DESIGN MAÇÔNICO
# ==========================================
st.set_page_config(page_title="Tesouraria - Jeronimo Rosado 1994", page_icon="🏛️", layout="wide")

# ==========================================
# SISTEMA DE LOGIN
# ==========================================

# Função para verificar login
def verificar_login(email, senha):
    conn = sqlite3.connect(r'C:\Users\Rodrigo  Garcia\Desktop\Maconaria\financas_loja.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, email, senha, nivel_acesso, ativo FROM usuarios WHERE email = ?", (email,))
    usuario = cursor.fetchone()
    conn.close()
    
    if usuario:
        if usuario[5] == 0:
            return None, "Usuário desativado. Contate o administrador."
        if usuario[3] == senha:
            return {
                'id': usuario[0],
                'nome': usuario[1],
                'email': usuario[2],
                'nivel_acesso': usuario[4]
            }, None
        else:
            return None, "Senha incorreta."
    else:
        return None, "Usuário não encontrado."

# Se não estiver logado, mostrar tela de login
if 'usuario_logado' not in st.session_state or not st.session_state['usuario_logado']:
    # CSS personalizado para login
    st.markdown("""
        <style>
        .main {
            background: linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%);
            min-height: 100vh;
        }
        .login-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 5px 40px 40px 40px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            max-width: 450px;
            margin: 0 auto;
        }
        .stButton>button {
            background: linear-gradient(135deg, #d4af37 0%, #f4d03f 100%);
            color: #1e3a5f;
            font-weight: bold;
            border-radius: 10px;
            padding: 8px 16px;
            border: none;
            font-size: 14px;
        }
        .stTextInput>div>div>input {
            border-radius: 10px;
            border: 2px solid #e2e8f0;
            padding: 8px;
            font-size: 14px;
            width: 100%;
        }
        .stForm {
            margin: 0 auto;
            max-width: 350px;
        }
        .title {
            color: #1e3a5f;
            font-size: 2.5rem;
            font-weight: bold;
            text-align: center;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #64748b;
            text-align: center;
            margin-bottom: 30px;
        }
        .watermark {
            position: fixed;
            opacity: 0.03;
            font-size: 150px;
            font-weight: bold;
            color: #d4af37;
            z-index: 0;
            pointer-events: none;
        }
        .watermark-1 { top: 10%; left: 5%; transform: rotate(-15deg); }
        .watermark-2 { bottom: 10%; right: 5%; transform: rotate(15deg); }
        .watermark-3 { top: 50%; left: 50%; transform: translate(-50%, -50%); }
        </style>
    """, unsafe_allow_html=True)
    
    # Marcas d'água
    st.markdown("""
        <div class="watermark watermark-1">💰</div>
        <div class="watermark watermark-2">🏛️</div>
        <div class="watermark watermark-3">⚖️</div>
    """, unsafe_allow_html=True)
    
    # Container de login
    #st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # Logo
    try:
        col1, col2, col3 = st.columns([4, 3, 2])
        with col2:
            st.image("logo.png", width=180)
    except:
        pass
    
    st.markdown('<h1 class="title">🏛️ Sistema Financeiro</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Loja Jerônimo Rosado 1994</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    with st.form("login_form"):
        email = st.text_input("📧 E-mail", placeholder="Digite seu e-mail")
        senha = st.text_input("🔑 Senha", type="password", placeholder="Digite sua senha")
        submit_button = st.form_submit_button("Entrar", use_container_width=True)
    
    if submit_button:
        if email and senha:
            usuario, erro = verificar_login(email, senha)
            if usuario:
                st.session_state['usuario_logado'] = True
                st.session_state['usuario_nome'] = usuario['nome']
                st.session_state['usuario_email'] = usuario['email']
                st.session_state['usuario_nivel'] = usuario['nivel_acesso']
                st.session_state['usuario_id'] = usuario['id']
                st.success(f"Bem-vindo, {usuario['nome']}!")
                st.rerun()
            else:
                st.error(erro)
        else:
            st.error("Preencha todos os campos.")
    
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; color: #64748b; margin-top: 20px;">
            <p>🔒 Sistema Seguro de Gestão Financeira Maçônica</p>
            <p style="font-size: 0.8rem;">© 2026 Rodrigo Garcia Rebouças</p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# Customização de cores para manter a identidade Azul-Escuro e Dourado
st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #f8fafc; }
    h1, h2, h3 { color: #d4af37 !important; font-family: 'Poppins', sans-serif; }
    .stButton>button { background-color: #d4af37; color: #001f3f; font-weight: bold; border-radius: 5px; }
    .stButton>button:hover { background-color: #001f3f; color: #d4af37; border: 1px solid #d4af37; }
    div[data-testid="stMetricValue"] { color: #ffffff !important; }
    div[data-testid="stMetricLabel"] { color: #94a3b8 !important; }
    /* Cores de status fixas */
    .metric-receita { color: #22c55e !important; }
    .metric-despesa { color: #ef4444 !important; }
    .metric-saldo { color: #3b82f6 !important; }
    /* Melhoria na Tabela */
    .stDataFrame { border: 1px solid #e2e8f0; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CONFIGURAÇÃO DO BANCO DE DADOS (SQLITE)
# ==========================================
DB_PATH = r'C:\Users\Rodrigo  Garcia\Desktop\Maconaria\financas_loja.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS obreiros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cim TEXT DEFAULT '000000',
            grau TEXT NOT NULL,
            valor_mensalidade REAL NOT NULL,
            isento INTEGER DEFAULT 0,
            data_admissao TEXT DEFAULT '2026-01-01',
            data_nascimento TEXT,
            email TEXT,
            telefone TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            tipo TEXT NOT NULL,
            categoria TEXT NOT NULL,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            obreiro_id INTEGER,
            mes_competencia TEXT,
            ano_competencia TEXT,
            tipo_caixa TEXT DEFAULT 'Bancário',
            FOREIGN KEY (obreiro_id) REFERENCES obreiros(id) ON DELETE SET NULL
        )
    """)
    
    # Adicionar coluna tipo_caixa se não existir
    try:
        cursor.execute("ALTER TABLE transacoes ADD COLUMN tipo_caixa TEXT DEFAULT 'Bancário'")
    except sqlite3.OperationalError:
        pass  # A coluna já existe
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS noticias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            conteudo TEXT NOT NULL,
            data_publicacao TEXT NOT NULL,
            autor TEXT,
            ativo INTEGER DEFAULT 1
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descricao TEXT,
            data_evento TEXT NOT NULL,
            hora TEXT,
            local TEXT,
            tipo TEXT DEFAULT 'Geral'
        )
    """)
    
    # === Tabela espelho para receber os dados brutos da API do Sicredi ===
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            nivel_acesso TEXT DEFAULT 'usuario',
            ativo INTEGER DEFAULT 1,
            data_cadastro TEXT NOT NULL
        )
    """)
    
    # === Tabela espelho para receber os dados brutos da API do Sicredi ===
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fila_sicredi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_sicredi TEXT UNIQUE NOT NULL,
            data TEXT NOT NULL,
            tipo TEXT NOT NULL,
            descricao_banco TEXT NOT NULL,
            valor REAL NOT NULL,
            status_conciliacao TEXT DEFAULT 'Pendente'
        )
    """)
    
    # Adicionando o vínculo na tabela de transações para evitar duplicidade no Livro Caixa
    try:
        cursor.execute("ALTER TABLE transacoes ADD COLUMN id_sicredi TEXT UNIQUE")
    except sqlite3.OperationalError:
        pass  # A coluna já existe, segue o fluxo
    # ====================================================================
    
    cursor.execute("SELECT COUNT(*) FROM obreiros")
    if cursor.fetchone()[0] == 0:
        query_ins = """
            INSERT INTO obreiros (nome, cim, grau, valor_mensalidade, isento, data_admissao) 
            VALUES (?, ?, ?, ?, ?, ?)
        """
        valores = [
            ("Agenilton Goncalves de Lima", "336627", "Mestre", 162.00, 0, "2026-01-01"),
            ("Raimundo Nonato", "123456", "Mestre", 100.00, 0, "2026-01-01"),
            ("Antonio da Silva", "789101", "Companheiro", 100.00, 0, "2026-01-01")
        ]
        cursor.executemany(query_ins, valores)
    
    cursor.execute("SELECT COUNT(*) FROM categorias")
    if cursor.fetchone()[0] == 0:
        query_cat = """
            INSERT INTO categorias (nome) VALUES (?)
        """
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
        cursor.executemany(query_cat, [(cat,) for cat in categorias])
        
    conn.commit()
    cursor.close()
    conn.close()

init_db()

def buscar_dados(query, params=()):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, params)
    resultados = cursor.fetchall()
    colunas = [desc[0] for desc in cursor.description]
    cursor.close()
    conn.close()
    return pd.DataFrame(resultados, columns=colunas)

def executar_comando(query, params=()):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erro ao executar comando: {str(e)}")
        return False

# Funções auxiliares de formatação
def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def formatar_data(data_str):
    if isinstance(data_str, str):
        return datetime.strptime(data_str, '%Y-%m-%d').strftime('%d/%m/%Y')
    elif isinstance(data_str, datetime):
        return data_str.strftime('%d/%m/%Y')
    return data_str

# ==========================================
# 3. GERADOR DE FICHA FINANCEIRA EM PDF
# ==========================================
class PDF_Ficha(FPDF):
    def header(self):
        self.set_fill_color(0, 33, 71) 
        self.rect(10, 10, 277, 30, 'F')
        
        self.set_text_color(212, 175, 55) 
        self.set_font('Helvetica', 'B', 14)
        self.cell(0, 8, 'AUGUSTA RESPEITAVEL E BENFEITORA LOJA MACONICA', ln=True, align='C')
        self.set_font('Helvetica', 'B', 18)
        self.cell(0, 8, 'JERONIMO ROSADO - N 1994', ln=True, align='C')
        
        self.set_text_color(255, 255, 255)
        self.set_font('Helvetica', 'I', 10)
        self.cell(0, 6, 'FICHA FINANCEIRA ANUAL COMPLETA - EXERCICIO 2026', ln=True, align='C')
        self.ln(10)

def gerar_ficha_pdf(row_obreiro, ano_alvo="2026"):
    obreiro_id = row_obreiro['id']
    nome = row_obreiro['nome']
    cim = row_obreiro['cim']
    
    
    meses_lista = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    meses_siglas = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    
    categorias_ficha = [
        "Mensalidade Loja",
        "Fraternidade Feminina",
        "Auxilio Funeral (PAF)",
        "Anuidade GOB Federal",
        "Anuidade GOB RN",
        "Taxa Extra"
    ]
    
    df_trans = buscar_dados("""
        SELECT categoria, valor, mes_competencia 
        FROM transacoes 
        WHERE obreiro_id = ? AND ano_competencia = ? AND tipo = 'Entrada'
    """, (obreiro_id, ano_alvo))
    
    matriz = {cat: {mes: 0.0 for mes in meses_lista} for cat in categorias_ficha}
    
    # Mapeamento de meses em inglês para português
    meses_ingles_portugues = {
        'January': 'Janeiro', 'February': 'Fevereiro', 'March': 'Março',
        'April': 'Abril', 'May': 'Maio', 'June': 'Junho',
        'July': 'Julho', 'August': 'Agosto', 'September': 'Setembro',
        'October': 'Outubro', 'November': 'Novembro', 'December': 'Dezembro'
    }
    
    for _, trans in df_trans.iterrows():
        cat = trans['categoria']
        if "Mensalidade" in cat: cat_key = "Mensalidade Loja"
        elif "PAF" in cat or "Funeral" in cat: cat_key = "Auxilio Funeral (PAF)"
        elif "Federal" in cat: cat_key = "Anuidade GOB Federal"
        elif "RN" in cat: cat_key = "Anuidade GOB RN"
        elif "Feminina" in cat: cat_key = "Fraternidade Feminina"
        else: cat_key = "Taxa Extra"
        
        # Converter mês de inglês para português se necessário
        mes_comp = trans['mes_competencia']
        if mes_comp in meses_ingles_portugues:
            mes_comp = meses_ingles_portugues[mes_comp]
        
        if cat_key in matriz and mes_comp in meses_lista:
            matriz[cat_key][mes_comp] += float(trans['valor'])
            
    pdf = PDF_Ficha(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    pdf.set_fill_color(248, 250, 252)
    pdf.rect(10, 48, 277, 15, 'F')
    pdf.set_draw_color(0, 33, 71)
    pdf.line(10, 48, 10, 63)
    
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(100, 116, 139)
    pdf.text(14, 53, "NOME DO OBREIRO")
    pdf.text(160, 53, "CIM")
    
    
    pdf.set_text_color(0, 33, 71)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.text(14, 59, str(nome))
    pdf.text(160, 59, str(cim))
    
    
    pdf.ln(20)
    
    col_larguras = [45] + [18] * 12 + [16]
    pdf.set_fill_color(0, 33, 71)
    pdf.set_text_color(212, 175, 55)
    pdf.set_font('Helvetica', 'B', 9)
    
    pdf.cell(col_larguras[0], 8, "Obrigacoes (R$)", border=1, align='L', fill=True)
    for sigla in meses_siglas:
        pdf.cell(col_larguras[1], 8, sigla, border=1, align='C', fill=True)
    pdf.cell(col_larguras[-1], 8, "Total", border=1, align='C', fill=True)
    pdf.ln()
    
    pdf.set_text_color(30, 41, 59)
    totais_colunas = {mes: 0.0 for mes in meses_lista}
    total_geral_geral = 0.0
    
    for cat in categorias_ficha:
        pdf.set_font('Helvetica', 'B', 9)
        pdf.cell(col_larguras[0], 8, cat, border=1, align='L')
        pdf.set_font('Helvetica', '', 9)
        
        total_linha = 0.0
        for mes in meses_lista:
            val = matriz[cat][mes]
            total_linha += val
            totais_colunas[mes] += val
            val_str = f"{val:,.2f}".replace(".", ",") if val > 0 else "-"
            pdf.cell(col_larguras[1], 8, val_str, border=1, align='C')
            
        total_geral_geral += total_linha
        pdf.set_font('Helvetica', 'B', 9)
        t_lin_str = f"{total_linha:,.2f}".replace(".", ",") if total_linha > 0 else "-"
        pdf.cell(col_larguras[-1], 8, t_lin_str, border=1, align='C')
        pdf.ln()
        
    pdf.set_fill_color(255, 251, 235)
    pdf.set_text_color(146, 64, 14)
    pdf.set_font('Helvetica', 'B', 9)
    
    pdf.cell(col_larguras[0], 8, "TOTAL GERAL", border=1, align='L', fill=True)
    for mes in meses_lista:
        v_col = totais_colunas[mes]
        v_col_str = f"{v_col:,.2f}".replace(".", ",") if v_col > 0 else "0,00"
        pdf.cell(col_larguras[1], 8, v_col_str, border=1, align='C', fill=True)
        
    t_geral_str = f"{total_geral_geral:,.2f}".replace(".", ",")
    pdf.cell(col_larguras[-1], 8, t_geral_str, border=1, align='C', fill=True)
    
    pdf.ln(12)
    pdf.set_text_color(100, 116, 139)
    pdf.set_font('Helvetica', 'I', 9)
    pdf.cell(0, 5, "Oriente de Mossoro - RN | GOB-RN | Sistema de Tesouraria Integrado", ln=True, align='C')

    pdf.ln(12)
    pdf.set_text_color(100, 116, 139)
    pdf.set_font('Helvetica', 'I', 9)
    pdf.cell(0, 5, "GOB Federal: 210,00 (3x 70,00 Mar-Mai) | GOB RN: 338,00 (3x 112,66 Jun-Ago) | PAF: 130,00 (2x 65,00 Set-Out)", ln=True, align='C')
    
    pdf.ln(2)
    pdf.set_text_color(212, 175, 55)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 6, "T.F.A.", ln=True, align='C')
    
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# INTERFACE E NAVEGAÇÃO DO STREAMLIT
# ==========================================
st.title("🏛️ Sistema de Gestão Financeira — Loja Jerônimo Rosado 1994")
st.markdown("---")

st.sidebar.markdown("""
    <style>
    .sidebar-title {
        color: #d4af37;
        font-size: 1.4rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 2px solid #d4af37;
    }
    .user-info {
        color: #94a3b8;
        font-size: 0.9rem;
        margin: 5px 0;
    }
    </style>
    <h2 class="sidebar-title">🏛️ Menu de Navegação</h2>
""", unsafe_allow_html=True)

modulo = st.sidebar.radio("", [
    "📊 Visão Geral (Dashboard)",
    "📝 Livro Caixa (Lançar e Editar)",
    "🏦 Conciliação Bancária",
    "📈 Relatório Detalhado",
    "🏷️ Gerenciar Categorias",
    "💳 Carteira de Obreiros (Mensalidades)",
    "👤 Cadastro de Obreiros",
    "👥 Cadastro de Usuários",
    "📰 Notícias e Informações",
    "📅 Eventos e Agenda",
    "🎂 Aniversariantes",
    "💾 Backup e Restauração"
], label_visibility="collapsed")

st.sidebar.markdown("---")
st.sidebar.write(f"👤 Usuário: {st.session_state.get('usuario_nome', 'Desconhecido')}")
st.sidebar.write(f"🔑 Nível: {st.session_state.get('usuario_nivel', 'usuario').capitalize()}")

if st.sidebar.button("🚪 Sair (Logout)", use_container_width=True):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

MESES = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
ANOS = ["2026", "2027", "2028"]

# ==========================================
# MÓDULO 1: DASHBOARD FINANCEIRO REALTIME
# ==========================================
if modulo == "📊 Visão Geral (Dashboard)":
    st.subheader("📊 Painel Financeiro Consolidado")
    
    # Filtros de período e tipo de caixa
    col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
    with col_filtro1:
        data_inicio = st.date_input("Data Início", value=date(2026, 1, 1))
    with col_filtro2:
        data_fim = st.date_input("Data Fim", value=date.today())
    with col_filtro3:
        tipo_caixa_dash = st.selectbox("Tipo de Caixa:", ["Todos", "Bancário", "Dinheiro"])
    
    # Cálculo de Métricas Globais com filtro
    if tipo_caixa_dash == "Todos":
        query_dash = """
            SELECT data, tipo, categoria, descricao, valor, mes_competencia, ano_competencia, tipo_caixa
            FROM transacoes 
            WHERE data BETWEEN ? AND ?
        """
        params_dash = (data_inicio.strftime('%Y-%m-%d'), data_fim.strftime('%Y-%m-%d'))
    else:
        query_dash = """
            SELECT data, tipo, categoria, descricao, valor, mes_competencia, ano_competencia, tipo_caixa
            FROM transacoes 
            WHERE data BETWEEN ? AND ? AND tipo_caixa = ?
        """
        params_dash = (data_inicio.strftime('%Y-%m-%d'), data_fim.strftime('%Y-%m-%d'), tipo_caixa_dash)
    
    df_dash = buscar_dados(query_dash, params_dash)
    total_obreiros_cad = len(buscar_dados("SELECT id FROM obreiros"))
    
    if not df_dash.empty:
        df_dash['valor'] = pd.to_numeric(df_dash['valor'], errors='coerce').fillna(0.0)
        df_dash['data'] = pd.to_datetime(df_dash['data'])
        df_dash['tipo'] = df_dash['tipo'].astype(str).str.strip().replace('Saída', 'Saida').replace('Saida', 'Saida')
        
        total_entradas = df_dash[df_dash['tipo'] == 'Entrada']['valor'].sum()
        total_saidas = df_dash[df_dash['tipo'].isin(['Saída', 'Saida'])]['valor'].sum()
        saldo_caixa = total_entradas - total_saidas
        total_transacoes = len(df_dash)
        
        # Cards de KPI
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total de Entradas", formatar_moeda(total_entradas))
        col2.metric("Total de Saídas", formatar_moeda(total_saidas))
        col3.metric("Saldo Líquido", formatar_moeda(saldo_caixa),
                    delta=formatar_moeda(saldo_caixa), delta_color="normal" if saldo_caixa >= 0 else "inverse")
        col4.metric("Transações", f"{total_transacoes}")
        
        st.markdown("---")
        
        # Gráficos
        col_graf1, col_graf2 = st.columns(2)
        
        with col_graf1:
            st.subheader("📊 Receitas por Categoria")
            df_entradas = df_dash[df_dash['tipo'] == 'Entrada']
            if not df_entradas.empty:
                df_categoria_entradas = df_entradas.groupby('categoria')['valor'].sum().reset_index()
                df_categoria_entradas = df_categoria_entradas.sort_values('valor', ascending=True)
                fig_categoria_entradas = px.bar(df_categoria_entradas, x='valor', y='categoria',
                                      orientation='h', color='valor',
                                      color_continuous_scale='Greens')
                fig_categoria_entradas.update_layout(xaxis_title="Valor (R$)", yaxis_title="",
                                            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                            font=dict(color='#94a3b8'), margin=dict(t=20, b=20, l=0, r=0))
                st.plotly_chart(fig_categoria_entradas, use_container_width=True)
            else:
                st.info("Não há receitas no período selecionado")
        
        with col_graf2:
            st.subheader("📊 Despesas por Categoria")
            df_saidas = df_dash[df_dash['tipo'].isin(['Saída', 'Saida'])]
            if not df_saidas.empty:
                df_categoria = df_saidas.groupby('categoria')['valor'].sum().reset_index()
                df_categoria = df_categoria.sort_values('valor', ascending=True)
                fig_categoria = px.bar(df_categoria, x='valor', y='categoria',
                                      orientation='h', color='valor',
                                      color_continuous_scale='Reds')
                fig_categoria.update_layout(xaxis_title="Valor (R$)", yaxis_title="",
                                            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                            font=dict(color='#94a3b8'), margin=dict(t=20, b=20, l=0, r=0))
                st.plotly_chart(fig_categoria, use_container_width=True)
            else:
                st.info("Não há despesas no período selecionado")
        
        st.markdown("---")
        
        # Evolução mensal (novo do financeiro_old.py)
        st.subheader("📅 Evolução Mensal")
        df_dash['mes_ano'] = df_dash['data'].dt.to_period('M')
        df_mensal = df_dash.groupby(['mes_ano', 'tipo'])['valor'].sum().reset_index()
        df_mensal['mes_ano'] = df_mensal['mes_ano'].astype(str)
        
        if not df_mensal.empty:
            fig_evolucao = px.line(df_mensal, x='mes_ano', y='valor', color='tipo',
                                  color_discrete_map={'Entrada': '#22c55e', 'Saída': '#ef4444', 'Saida': '#ef4444'},
                                  markers=True)
            fig_evolucao.update_layout(xaxis_title="Mês/Ano", yaxis_title="Valor (R$)",
                                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                      font=dict(color='#94a3b8'), margin=dict(t=20, b=20, l=0, r=0))
            st.plotly_chart(fig_evolucao, use_container_width=True)
        else:
            st.info("Não há dados suficientes para gerar o gráfico de evolução mensal")
        
        st.markdown("---")
        
        # Filtro e visualização do Livro Caixa
        st.subheader("📜 Extrato Detalhado (Livro Caixa)")
        df_exibicao = df_dash.sort_values(by="data", ascending=False).copy()
        df_exibicao['data'] = df_exibicao['data'].dt.strftime('%d/%m/%Y')
        df_exibicao['valor'] = df_exibicao['valor'].apply(formatar_moeda)
        
        # Garantir que tipo_caixa exista e tenha valor padrão
        if 'tipo_caixa' not in df_exibicao.columns:
            df_exibicao['tipo_caixa'] = 'Bancário'
        df_exibicao['tipo_caixa'] = df_exibicao['tipo_caixa'].fillna('Bancário')

        # Renomear colunas específicas
        df_exibicao = df_exibicao.rename(columns={
            'data': 'Data',
            'tipo': 'Tipo',
            'categoria': 'Categoria',
            'descricao': 'Descrição / Favorecido',
            'tipo_caixa': 'Caixa',
            'valor': 'Valor (R$)'
        })

        st.dataframe(df_exibicao[["Data", "Tipo", "Categoria", "Descrição / Favorecido", "Caixa", "Valor (R$)"]],
                    use_container_width=True, height=400)
        
        st.write("### Exportar Balancete")
        df_export = df_dash[['data', 'tipo', 'categoria', 'descricao', 'valor']].copy()
        csv_data = df_export.to_csv(index=False, sep=';', encoding='utf-8-sig')
        
        st.download_button(
            label="📊 Baixar Relatório Balancete (CSV/Excel)",
            data=csv_data,
            file_name=f"Balancete_{data_inicio.strftime('%Y-%m-%d')}_a_{data_fim.strftime('%Y-%m-%d')}.csv",
            mime="text/csv",
            key="btn_export_dash"
        )
    else:
        st.info(f"Nenhum registro financeiro encontrado para o período de {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}.")

elif modulo == "🏷️ Gerenciar Categorias":
    st.subheader("Configuracao de Categorias")
    
    # Cadastro de nova categoria
    with st.form("form_nova_cat"):
        nome_cat = st.text_input("Nome da nova categoria:")
        if st.form_submit_button("Cadastrar Categoria"):
            if nome_cat.strip() != "":
                resultado = executar_comando("INSERT INTO categorias (nome) VALUES (?)", (nome_cat.strip(),))
                if resultado:
                    st.success("Categoria cadastrada com sucesso!")
                    st.rerun()
                else:
                    st.error("Erro ao cadastrar categoria. Possivelmente já existe.")
            else:
                st.error("O nome da categoria não pode estar vazio.")
    
    st.markdown("---")
    
    # Listagem e Exclusão
    df_cats = buscar_dados("SELECT id, nome FROM categorias ORDER BY nome")
    if not df_cats.empty:
        st.write("### Categorias Existentes")
        st.dataframe(df_cats, use_container_width=True, hide_index=True)
        
        st.write("### Excluir Categoria")
        with st.expander("Área de Exclusão"):
            cat_para_excluir = st.selectbox("Selecione a categoria para excluir:", df_cats['nome'].tolist())
            if st.button("Confirmar Exclusão", type="secondary"):
                if cat_para_excluir:
                    resultado = executar_comando("DELETE FROM categorias WHERE nome = ?", (cat_para_excluir,))
                    if resultado:
                        st.success(f"Categoria '{cat_para_excluir}' excluída com sucesso!")
                        st.rerun()
                    else:
                        st.error("Erro ao excluir categoria.")
    else:
        st.info("Nenhuma categoria cadastrada.")
        
elif modulo == "📝 Livro Caixa (Lançar e Editar)":
    st.subheader("Lancamentos no Livro do Caixa")
    
    # Seleção do tipo de caixa
    tipo_caixa_sel = st.radio("Tipo de Caixa:", ["Bancário", "Dinheiro"], horizontal=True)

    # Busca categorias do banco
    df_cats = buscar_dados("SELECT nome FROM categorias ORDER BY nome")
    lista_cats = df_cats['nome'].tolist() if not df_cats.empty else ["Outros"]

    with st.form("form_caixa"):
        dat = st.date_input("Data")
        tip = st.selectbox("Tipo", ["Saída", "Entrada"])
        cat = st.selectbox("Categoria", lista_cats)
        desc = st.text_input("Descricao / Credor")
        val = st.number_input("Valor", min_value=0.01, step=0.01)

        if st.form_submit_button("Lancar"):
            if val > 0:
                if not desc.strip():
                    desc = f"{tip} - {cat}"
                resultado = executar_comando("INSERT INTO transacoes (data, tipo, categoria, descricao, valor, mes_competencia, ano_competencia, tipo_caixa) VALUES (?,?,?,?,?,?,?,?)",
                                 (dat.strftime('%Y-%m-%d'), tip, cat, desc, val, dat.strftime('%B'), dat.strftime('%Y'), tipo_caixa_sel))
                if resultado:
                    st.success("Lancado!")
                    st.rerun()
            else:
                st.error("O valor deve ser maior que zero.")

    st.markdown("---")
    st.subheader("Historico de Lancamentos Recentes")
    
    # Filtro por tipo de caixa no histórico
    filtro_caixa_hist = st.selectbox("Filtrar por Tipo de Caixa:", ["Todos", "Bancário", "Dinheiro"], key="filtro_hist_caixa")
    
    if filtro_caixa_hist == "Todos":
        df_lista_trans = buscar_dados("SELECT id, data, tipo, categoria, descricao, valor, tipo_caixa FROM transacoes ORDER BY id DESC")
    else:
        df_lista_trans = buscar_dados("SELECT id, data, tipo, categoria, descricao, valor, tipo_caixa FROM transacoes WHERE tipo_caixa = ? ORDER BY id DESC", (filtro_caixa_hist,))
    
    if not df_lista_trans.empty:
        df_visualizacao = df_lista_trans.copy()
        df_visualizacao['valor'] = df_visualizacao['valor'].apply(lambda x: f"R$ {float(x):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        
        # Renomear colunas para exibição amigável
        df_visualizacao = df_visualizacao.rename(columns={
            'id': 'ID',
            'data': 'Data',
            'tipo': 'Tipo',
            'categoria': 'Categoria',
            'descricao': 'Descrição',
            'valor': 'Valor',
            'tipo_caixa': 'Caixa'
        })
        
        st.dataframe(df_visualizacao[["ID", "Data", "Tipo", "Categoria", "Descrição", "Caixa", "Valor"]], use_container_width=True, hide_index=True)
        
        with st.expander("Remover Lancamento Duplicado ou Incorreto"):
            id_para_deletar = st.number_input("Digite o ID do lancamento que deseja excluir:", min_value=1, step=1)
            if st.button("Confirmar Exclusao do Lancamento"):
                if id_para_deletar in df_lista_trans['id'].values:
                    executar_comando("DELETE FROM transacoes WHERE id = ?", (int(id_para_deletar),))
                    st.success("Lancamento removido com sucesso!")
                    st.rerun()
                else:
                    st.error("ID nao encontrado no historico atual.")
    else:
        st.info("Nenhum lancamento encontrado no Livro Caixa.")

# ==========================================
# MÓDULO NOVO: CONCILIAÇÃO BANCÁRIA
# ==========================================
elif modulo == "🏦 Conciliação Bancária":
    st.subheader("Auditoria e Conciliação Bancária (Sicredi)")
    st.write("Lançamentos vindos da API aguardando classificação para entrar no Livro Caixa.")

    df_pendentes = buscar_dados("SELECT * FROM fila_sicredi WHERE status_conciliacao = 'Pendente'")
    df_cats = buscar_dados("SELECT nome FROM categorias ORDER BY nome")
    lista_cats = df_cats['nome'].tolist() if not df_cats.empty else ["Outros"]

    if not df_pendentes.empty:
        for index, row in df_pendentes.iterrows():
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 3, 2, 2])
                
                with col1:
                    st.write(f"**Data:** {formatar_data(row['data'])}")
                    st.write(f"**Tipo:** {row['tipo']}")
                
                with col2:
                    st.write(f"**Descrição API:** {row['descricao_banco']}")
                    st.write(f"**Valor:** {formatar_moeda(row['valor'])}")
                
                with col3:
                    cat_selecionada = st.selectbox(
                        "Classificar na Categoria:",
                        lista_cats,
                        key=f"cat_api_{row['id']}"
                    )
                
                with col4:
                    st.write("") # Espaçamento para alinhar os botões
                    col_btn1, col_btn2 = st.columns(2)
                    
                    with col_btn1:
                        if st.button("Confirmar", key=f"btn_conf_{row['id']}", use_container_width=True):
                            data_formatada = datetime.strptime(row['data'], '%Y-%m-%d')
                            mes_comp = data_formatada.strftime('%B')
                            ano_comp = data_formatada.strftime('%Y')

                            # Insere no Livro Caixa oficial
                            sucesso = executar_comando(
                                "INSERT INTO transacoes (data, tipo, categoria, descricao, valor, mes_competencia, ano_competencia, id_sicredi, tipo_caixa) VALUES (?,?,?,?,?,?,?,?,?)",
                                (row['data'], row['tipo'], cat_selecionada, row['descricao_banco'], row['valor'], mes_comp, ano_comp, row['id_sicredi'], 'Bancário')
                            )
                            
                            if sucesso:
                                # Marca como processado na fila
                                executar_comando("UPDATE fila_sicredi SET status_conciliacao = 'Conciliado' WHERE id = ?", (row['id'],))
                                st.success("Transação transferida para o Livro Caixa com sucesso!")
                                st.rerun()
                    
                    with col_btn2:
                        if st.button("Excluir", key=f"btn_exc_{row['id']}", type="secondary", use_container_width=True):
                            executar_comando("DELETE FROM fila_sicredi WHERE id = ?", (row['id'],))
                            st.success("Lançamento excluído da fila!")
                            st.rerun()
                            
            st.markdown("---")
    else:
        st.info("Nenhuma transação pendente. O caixa está atualizado com o banco.")

# ==========================================
# MÓDULO NOVO: RELATÓRIO DETALHADO
# ==========================================
elif modulo == "📈 Relatório Detalhado":
    st.subheader("📊 Relatório Detalhado do Caixa")
    
    # CSS personalizado para melhorar visualização do relatório
    st.markdown("""
        <style>
        .relatorio-container {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
        }
        .stDataFrame {
            border-radius: 8px;
            overflow: hidden;
        }
        .stDataFrame [data-testid="stDataFrame"] {
            background-color: rgba(255, 255, 255, 0.1);
        }
        .stDataFrame [data-testid="stDataFrame"] thead th {
            background-color: #d4af37;
            color: #1e3a5f;
            font-weight: bold;
            text-align: center;
            padding: 12px;
        }
        .stDataFrame [data-testid="stDataFrame"] tbody tr {
            border-bottom: 1px solid rgba(212, 175, 55, 0.2);
        }
        .stDataFrame [data-testid="stDataFrame"] tbody tr:hover {
            background-color: rgba(212, 175, 55, 0.1);
        }
        .stDataFrame [data-testid="stDataFrame"] td {
            padding: 10px;
            text-align: center;
        }
        .stMetric {
            background: linear-gradient(135deg, rgba(212, 175, 55, 0.2) 0%, rgba(212, 175, 55, 0.1) 100%);
            border: 1px solid rgba(212, 175, 55, 0.3);
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
        }
        .stMetric [data-testid="stMetricValue"] {
            color: #d4af37 !important;
            font-size: 24px;
            font-weight: bold;
        }
        .stMetric [data-testid="stMetricLabel"] {
            color: #94a3b8 !important;
            font-size: 14px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Seleção de período
    col_data1, col_data2 = st.columns(2)
    with col_data1:
        data_inicio_rel = st.date_input("Data Início", value=date(2026, 1, 1))
    with col_data2:
        data_fim_rel = st.date_input("Data Fim", value=date.today())
    
    # Filtro por tipo de caixa
    tipo_caixa_rel = st.selectbox("Tipo de Caixa:", ["Todos", "Bancário", "Dinheiro"])
    
    # Buscar dados do período
    if tipo_caixa_rel == "Todos":
        query_rel = """
            SELECT data, tipo, categoria, descricao, valor, mes_competencia, ano_competencia, tipo_caixa
            FROM transacoes 
            WHERE data BETWEEN ? AND ?
            ORDER BY data
        """
        params_rel = (data_inicio_rel.strftime('%Y-%m-%d'), data_fim_rel.strftime('%Y-%m-%d'))
    else:
        query_rel = """
            SELECT data, tipo, categoria, descricao, valor, mes_competencia, ano_competencia, tipo_caixa
            FROM transacoes 
            WHERE data BETWEEN ? AND ? AND tipo_caixa = ?
            ORDER BY data
        """
        params_rel = (data_inicio_rel.strftime('%Y-%m-%d'), data_fim_rel.strftime('%Y-%m-%d'), tipo_caixa_rel)
    
    df_rel = buscar_dados(query_rel, params_rel)
    
    if not df_rel.empty:
        df_rel['valor'] = pd.to_numeric(df_rel['valor'], errors='coerce').fillna(0.0)
        df_rel['data'] = pd.to_datetime(df_rel['data'])
        df_rel['mes_ano'] = df_rel['data'].dt.to_period('M')
        
        # Gerar relatório mês a mês
        st.markdown("---")
        st.write("### Relatório Mês a Mês")
        
        meses_periodo = sorted(df_rel['mes_ano'].unique())
        
        relatorio_completo = []
        
        # Mapeamento de meses em inglês para português
        meses_ingles_portugues = {
            'January': 'Janeiro', 'February': 'Fevereiro', 'March': 'Março',
            'April': 'Abril', 'May': 'Maio', 'June': 'Junho',
            'July': 'Julho', 'August': 'Agosto', 'September': 'Setembro',
            'October': 'Outubro', 'November': 'Novembro', 'December': 'Dezembro'
        }
        
        for mes_ano in meses_periodo:
            df_mes = df_rel[df_rel['mes_ano'] == mes_ano]
            mes_nome_ingles = mes_ano.strftime('%B/%Y')
            mes_partes = mes_nome_ingles.split('/')
            mes_portugues = meses_ingles_portugues.get(mes_partes[0], mes_partes[0])
            mes_nome = f"{mes_portugues}/{mes_partes[1]}"
            
            with st.expander(f"📅 {mes_nome.upper()}"):
                # Entradas por categoria
                df_entradas_mes = df_mes[df_mes['tipo'] == 'Entrada']
                if not df_entradas_mes.empty:
                    st.markdown('<div class="relatorio-container">', unsafe_allow_html=True)
                    st.markdown('<h3 style="color: #d4af37; margin-bottom: 15px;">💰 Entradas por Categoria</h3>', unsafe_allow_html=True)
                    
                    # Mostrar tabela com todos os lançamentos
                    df_entradas_display = df_entradas_mes[['data', 'categoria', 'descricao', 'valor']].copy()
                    df_entradas_display['data'] = df_entradas_display['data'].apply(formatar_data)
                    df_entradas_display['valor'] = df_entradas_display['valor'].apply(formatar_moeda)
                    df_entradas_display.columns = ['Data', 'Categoria', 'Descrição', 'Valor']
                    st.dataframe(df_entradas_display, use_container_width=True, hide_index=True)
                    
                    total_entradas = df_entradas_mes['valor'].sum()
                    col_entradas = st.columns([1, 2, 1])
                    with col_entradas[1]:
                        st.metric("Total Entradas", formatar_moeda(total_entradas))
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.info("Nenhuma entrada neste mês")
                
                st.markdown("---")
                
                # Saídas por categoria
                df_saidas_mes = df_mes[df_mes['tipo'].isin(['Saída', 'Saida'])]
                if not df_saidas_mes.empty:
                    st.markdown('<div class="relatorio-container">', unsafe_allow_html=True)
                    st.markdown('<h3 style="color: #d4af37; margin-bottom: 15px;">💸 Saídas por Categoria</h3>', unsafe_allow_html=True)
                    
                    # Mostrar tabela com todos os lançamentos
                    df_saidas_display = df_saidas_mes[['data', 'categoria', 'descricao', 'valor']].copy()
                    df_saidas_display['data'] = df_saidas_display['data'].apply(formatar_data)
                    df_saidas_display['valor'] = df_saidas_display['valor'].apply(formatar_moeda)
                    df_saidas_display.columns = ['Data', 'Categoria', 'Descrição', 'Valor']
                    st.dataframe(df_saidas_display, use_container_width=True, hide_index=True)
                    
                    total_saidas = df_saidas_mes['valor'].sum()
                    col_saidas = st.columns([1, 2, 1])
                    with col_saidas[1]:
                        st.metric("Total Saídas", formatar_moeda(total_saidas))
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.info("Nenhuma saída neste mês")
                
                st.markdown("---")
                
                # Saldo do mês
                st.markdown('<div class="relatorio-container">', unsafe_allow_html=True)
                st.markdown('<h3 style="color: #d4af37; margin-bottom: 15px;">⚖️ Saldo do Mês</h3>', unsafe_allow_html=True)
                saldo_mes = total_entradas - total_saidas if not df_entradas_mes.empty and not df_saidas_mes.empty else (total_entradas if not df_entradas_mes.empty else -total_saidas)
                col_saldo = st.columns([1, 2, 1])
                with col_saldo[1]:
                    st.metric("Saldo do Mês", formatar_moeda(saldo_mes), delta_color="normal" if saldo_mes >= 0 else "inverse")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Adicionar ao relatório completo para exportação
                for _, row in df_entradas_mes.iterrows():
                    relatorio_completo.append({
                        'Mês': mes_nome,
                        'Tipo': 'Entrada',
                        'Data': row['data'],
                        'Categoria': row['categoria'],
                        'Descrição': row['descricao'],
                        'Valor': row['valor'],
                        'Caixa': row['tipo_caixa']
                    })
                for _, row in df_saidas_mes.iterrows():
                    relatorio_completo.append({
                        'Mês': mes_nome,
                        'Tipo': 'Saída',
                        'Data': row['data'],
                        'Categoria': row['categoria'],
                        'Descrição': row['descricao'],
                        'Valor': row['valor'],
                        'Caixa': row['tipo_caixa']
                    })
        
        # Exportar relatório completo em PDF
        st.markdown("---")
        st.write("### Exportar Relatório Completo")
        
        def gerar_pdf_relatorio(relatorio, data_inicio, data_fim):
            pdf = FPDF()
            pdf.add_page()
            
            # Cores personalizadas
            cor_dourado = (212, 175, 55)
            cor_azul_escuro = (30, 58, 95)
            cor_cinza = (148, 163, 184)
            
            # Cabeçalho com fundo dourado
            pdf.set_fill_color(*cor_dourado)
            pdf.rect(0, 0, 210, 40, 'F')
            
            # Título principal
            pdf.set_font('Arial', 'B', 20)
            pdf.set_text_color(30, 58, 95)
            pdf.cell(0, 15, 'Relatorio Detalhado do Caixa', 0, 1, 'C')
            
            # Subtítulo com período
            pdf.set_font('Arial', '', 12)
            pdf.set_text_color(30, 58, 95)
            pdf.cell(0, 10, f'Periodo: {data_inicio.strftime("%d/%m/%Y")} a {data_fim.strftime("%d/%m/%Y")}', 0, 1, 'C')
            
            # Linha decorativa
            pdf.ln(5)
            pdf.set_draw_color(*cor_dourado)
            pdf.set_line_width(0.5)
            pdf.line(20, 45, 190, 45)
            pdf.ln(10)
            
            # Agrupar por mês
            meses = sorted(set(item['Mês'] for item in relatorio))
            
            for mes in meses:
                # Cabeçalho do mês com fundo
                pdf.set_fill_color(30, 58, 95)
                pdf.set_text_color(255, 255, 255)
                pdf.set_font('Arial', 'B', 14)
                pdf.cell(0, 12, mes.upper(), 0, 1, 'L', True)
                pdf.ln(5)
                
                # Entradas
                pdf.set_text_color(212, 175, 55)
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 8, 'ENTRADAS', 0, 1, 'L')
                pdf.set_text_color(0, 0, 0)
                pdf.set_font('Arial', '', 10)
                
                entradas_mes = [item for item in relatorio if item['Mês'] == mes and item['Tipo'] == 'Entrada']
                if entradas_mes:
                    # Cabeçalho da tabela
                    pdf.set_fill_color(212, 175, 55)
                    pdf.set_text_color(30, 58, 95)
                    pdf.set_font('Arial', 'B', 9)
                    pdf.cell(30, 7, 'Data', 0, 0, 'C', True)
                    pdf.cell(50, 7, 'Categoria', 0, 0, 'C', True)
                    pdf.cell(80, 7, 'Descricao', 0, 0, 'C', True)
                    pdf.cell(30, 7, 'Valor', 0, 1, 'C', True)
                    pdf.ln(2)
                    
                    # Linhas da tabela
                    pdf.set_text_color(0, 0, 0)
                    pdf.set_font('Arial', '', 8)
                    for item in entradas_mes:
                        data_formatada = item['Data'].strftime('%d/%m/%Y') if hasattr(item['Data'], 'strftime') else str(item['Data'])
                        pdf.cell(30, 6, data_formatada, 0, 0, 'C')
                        pdf.cell(50, 6, item['Categoria'][:25] if item['Categoria'] else '', 0, 0, 'L')
                        pdf.cell(80, 6, item['Descrição'][:40] if item['Descrição'] else '', 0, 0, 'L')
                        pdf.cell(30, 6, f'R$ {item["Valor"]:.2f}', 0, 1, 'R')
                    
                    total_entradas = sum(item['Valor'] for item in entradas_mes)
                    pdf.ln(3)
                    pdf.set_text_color(212, 175, 55)
                    pdf.set_font('Arial', 'B', 11)
                    pdf.cell(0, 8, f'Total Entradas: R$ {total_entradas:.2f}', 0, 1, 'L')
                else:
                    pdf.set_text_color(148, 163, 184)
                    pdf.cell(0, 6, 'Nenhuma entrada', 0, 1, 'L')
                
                pdf.ln(8)
                
                # Saídas
                pdf.set_text_color(212, 175, 55)
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 8, 'SAIDAS', 0, 1, 'L')
                pdf.set_text_color(0, 0, 0)
                pdf.set_font('Arial', '', 10)
                
                saidas_mes = [item for item in relatorio if item['Mês'] == mes and item['Tipo'] == 'Saída']
                if saidas_mes:
                    # Cabeçalho da tabela
                    pdf.set_fill_color(212, 175, 55)
                    pdf.set_text_color(30, 58, 95)
                    pdf.set_font('Arial', 'B', 9)
                    pdf.cell(30, 7, 'Data', 0, 0, 'C', True)
                    pdf.cell(50, 7, 'Categoria', 0, 0, 'C', True)
                    pdf.cell(80, 7, 'Descricao', 0, 0, 'C', True)
                    pdf.cell(30, 7, 'Valor', 0, 1, 'C', True)
                    pdf.ln(2)
                    
                    # Linhas da tabela
                    pdf.set_text_color(0, 0, 0)
                    pdf.set_font('Arial', '', 8)
                    for item in saidas_mes:
                        data_formatada = item['Data'].strftime('%d/%m/%Y') if hasattr(item['Data'], 'strftime') else str(item['Data'])
                        pdf.cell(30, 6, data_formatada, 0, 0, 'C')
                        pdf.cell(50, 6, item['Categoria'][:25] if item['Categoria'] else '', 0, 0, 'L')
                        pdf.cell(80, 6, item['Descrição'][:40] if item['Descrição'] else '', 0, 0, 'L')
                        pdf.cell(30, 6, f'R$ {item["Valor"]:.2f}', 0, 1, 'R')
                    
                    total_saidas = sum(item['Valor'] for item in saidas_mes)
                    pdf.ln(3)
                    pdf.set_text_color(212, 175, 55)
                    pdf.set_font('Arial', 'B', 11)
                    pdf.cell(0, 8, f'Total Saidas: R$ {total_saidas:.2f}', 0, 1, 'L')
                else:
                    pdf.set_text_color(148, 163, 184)
                    pdf.cell(0, 6, 'Nenhuma saida', 0, 1, 'L')
                
                pdf.ln(8)
                
                # Saldo do mês com destaque
                saldo_mes = sum(item['Valor'] for item in entradas_mes) - sum(item['Valor'] for item in saidas_mes)
                pdf.set_fill_color(212, 175, 55)
                pdf.set_text_color(30, 58, 95)
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, f'Saldo do Mes: R$ {saldo_mes:.2f}', 0, 1, 'L', True)
                pdf.set_text_color(0, 0, 0)
                
                pdf.ln(10)
                
                # Linha separadora entre meses
                pdf.set_draw_color(212, 175, 55)
                pdf.set_line_width(0.3)
                pdf.line(20, pdf.get_y(), 190, pdf.get_y())
                pdf.ln(10)
            
            return pdf.output(dest='S').encode('latin-1')
        
        pdf_data = gerar_pdf_relatorio(relatorio_completo, data_inicio_rel, data_fim_rel)
        
        st.download_button(
            label="📊 Baixar Relatório Detalhado (PDF)",
            data=pdf_data,
            file_name=f"Relatorio_Detalhado_{data_inicio_rel.strftime('%Y-%m-%d')}_a_{data_fim_rel.strftime('%Y-%m-%d')}.pdf",
            mime="application/pdf",
            key="btn_export_relatorio"
        )
    else:
        st.info(f"Nenhum registro encontrado para o período de {data_inicio_rel.strftime('%d/%m/%Y')} a {data_fim_rel.strftime('%d/%m/%Y')}.")

# ==========================================
# MÓDULO 3: CARTEIRA DE OBREIROS & RELATÓRIO DE INADIMPLÊNCIA
# ==========================================
elif modulo == "💳 Carteira de Obreiros (Mensalidades)":
    st.subheader("Ficha Financeira de Obreiros e Inadimplencia")
    
    aba_status, aba_baixa, aba_inad = st.tabs(["Situacao de Regularidade", "Baixa Completa", "Relatorio de Inadimplencia"])
    
    with aba_status:
        st.write("### Consultar Ficha do Obreiro")
        df_obs = buscar_dados("SELECT * FROM obreiros ORDER BY nome")
        
        if not df_obs.empty:
            opcoes_busca = {f"{row['nome']} (CIM: {row['cim']})": row for _, row in df_obs.iterrows()}
            membro_selecionado = st.selectbox("Selecione o irmao:", ["Selecione..."] + list(opcoes_busca.keys()))
            
            if membro_selecionado != "Selecione...":
                row = opcoes_busca[membro_selecionado]
                st.write(f"### {row['nome']}")
                st.write(f"CIM: {row['cim']} | Grau: {row['grau']}")
                
                df_p = buscar_dados("SELECT mes_competencia, categoria, valor FROM transacoes WHERE obreiro_id = ? AND tipo = 'Entrada' ORDER BY id DESC", (row['id'],))
                
                if not df_p.empty:
                    st.dataframe(df_p, use_container_width=True)
                else:
                    st.info("Nenhum registro encontrado.")
                
                # Botao de emissao de ficha restaurado
                pdf_bytes = gerar_ficha_pdf(row, "2026")
                st.download_button(
                    label="Baixar Ficha Anual (PDF)", 
                    data=pdf_bytes, 
                    file_name=f"Ficha_{row['nome'].replace(' ', '_')}.pdf", 
                    mime="application/pdf"
                )

    with aba_baixa:
        st.write("### Recebimento de Mensalidades e Taxas")
        df_obs_Ativos = buscar_dados("SELECT id, nome, valor_mensalidade FROM obreiros ORDER BY nome")
        if not df_obs_Ativos.empty:
            dict_ativos = dict(zip(df_obs_Ativos['nome'], df_obs_Ativos['id']))
            dict_valores = dict(zip(df_obs_Ativos['nome'], df_obs_Ativos['valor_mensalidade']))
            
            irmao_sel = st.selectbox("Escolha o Obreiro:", list(dict_ativos.keys()))
            id_irmao = dict_ativos[irmao_sel]
            
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                mes_b = st.selectbox("Mes", MESES)
                ano_b = st.selectbox("Ano", ANOS)
            with col_b2:
                val_m = st.number_input("Mensalidade Loja", value=float(dict_valores[irmao_sel]))
                val_fem = st.number_input("Fraternidade Feminina", value=0.0)
            
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                val_paf = st.number_input("Auxilio Funeral PAF", value=10.84)
                val_fed = st.number_input("Anuidade GOB Federal", value=17.50)
            with col_t2:
                val_rn = st.number_input("Anuidade GOB RN", value=28.17)
                val_extra = st.number_input("Taxa Extra", value=0.0)
                nome_extra = st.text_input("Nome da Taxa Extra (opcional)", value="", placeholder="Ex: Taxa de Evento, Taxa de Jantar, etc.")
            
            # Verificacao de duplicidade
            ja_lancado = buscar_dados("SELECT id, categoria FROM transacoes WHERE obreiro_id = ? AND mes_competencia = ? AND ano_competencia = ?", (id_irmao, mes_b, ano_b))
            processar = True
            if not ja_lancado.empty:
                categorias_lancadas = ", ".join(ja_lancado['categoria'].tolist())
                st.warning(f"Este mes ja tem lancamentos: {categorias_lancadas}")
                processar = st.checkbox("Confirmar: Lancar duplicado mesmo assim")
            
            if st.button("Confirmar Lancamento da Baixa"):
                if processar:
                    pagamentos = [
                        ("Mensalidade Loja", val_m), ("Fraternidade Feminina", val_fem),
                        ("Auxilio Funeral (PAF)", val_paf), ("Anuidade GOB Federal", val_fed),
                        ("Anuidade GOB RN", val_rn), ("Taxa Extra", val_extra)
                    ]
                    for cat, val in pagamentos:
                        if val > 0:
                            # Usar nome personalizado para Taxa Extra
                            categoria_final = cat
                            if cat == "Taxa Extra" and nome_extra.strip():
                                categoria_final = nome_extra.strip()
                            
                            # Converter mês selecionado para número
                            meses_num = {
                                'Janeiro': 1, 'Fevereiro': 2, 'Março': 3, 'Abril': 4,
                                'Maio': 5, 'Junho': 6, 'Julho': 7, 'Agosto': 8,
                                'Setembro': 9, 'Outubro': 10, 'Novembro': 11, 'Dezembro': 12
                            }
                            mes_num = meses_num.get(mes_b, 1)
                            # Usar o último dia do mês selecionado como data do lançamento
                            data_lancamento = date(int(ano_b), mes_num, 1).strftime('%Y-%m-%d')
                            
                            descricao = f'Entrada/{irmao_sel}/{categoria_final}/{val}'
                            executar_comando("INSERT INTO transacoes (data, tipo, categoria, descricao, valor, obreiro_id, mes_competencia, ano_competencia, tipo_caixa) VALUES (?, 'Entrada', ?, ?, ?, ?, ?, ?, 'Bancário')",
                                             (data_lancamento, categoria_final, descricao, val, id_irmao, mes_b, ano_b))
                    st.success("Lancamento efetuado com sucesso.")
                    st.rerun()

    with aba_inad:
        st.write("### Auditoria de Inadimplencia")
        periodo_sel = st.selectbox("Filtrar por:", ["Ultimos 3 meses", "Ultimos 6 meses", "1 ano"])
        
        if st.button("Gerar Relatorio de Inadimplencia"):
            hoje = date.today()
            
            # Definir número de meses para verificação
            if "3 meses" in periodo_sel:
                meses_verificar = 3
            elif "6 meses" in periodo_sel:
                meses_verificar = 6
            else:
                meses_verificar = 12
            
            # Buscar obreiros não isentos
            df_obreiros = buscar_dados("SELECT id, nome, cim FROM obreiros WHERE isento = 0")
            
            inadimplentes = []
            
            for _, row_obreiro in df_obreiros.iterrows():
                obreiro_id = row_obreiro['id']
                obreiro_nome = row_obreiro['nome']
                
                # Buscar a última mensalidade paga - lógica híbrida
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                
                # Tentar primeiro por obreiro_id
                query_ultima_id = """
                    SELECT MAX(data)
                    FROM transacoes
                    WHERE obreiro_id = ? 
                    AND descricao LIKE '%Mensalidade Loja%'
                """
                cursor.execute(query_ultima_id, (obreiro_id,))
                resultado = cursor.fetchone()
                
                # Se não encontrar por ID, tentar por nome na descrição
                if not resultado or not resultado[0]:
                    query_ultima_nome = """
                        SELECT MAX(data)
                        FROM transacoes
                        WHERE descricao LIKE ? 
                        AND descricao LIKE '%Mensalidade Loja%'
                    """
                    cursor.execute(query_ultima_nome, (f'%{obreiro_nome}%',))
                    resultado = cursor.fetchone()
                
                conn.close()
                
                if resultado and resultado[0]:
                    ultima_data = resultado[0]
                    # Converter string de data para objeto date
                    if isinstance(ultima_data, str):
                        ultima_data = datetime.strptime(ultima_data, '%Y-%m-%d').date()
                    
                    # Calcular meses desde a última mensalidade
                    meses_desde_pagamento = (hoje.year - ultima_data.year) * 12 + (hoje.month - ultima_data.month)
                    
                    # Se a última mensalidade foi há mais meses que o período selecionado
                    if meses_desde_pagamento >= meses_verificar:
                        inadimplentes.append({
                            'nome': row_obreiro['nome'],
                            'cim': row_obreiro['cim'],
                            'ultima_mensalidade': ultima_data.strftime('%d/%m/%Y'),
                            'meses_atraso': meses_desde_pagamento
                        })
                else:
                    # Nunca pagou mensalidade
                    inadimplentes.append({
                        'nome': row_obreiro['nome'],
                        'cim': row_obreiro['cim'],
                        'ultima_mensalidade': 'Nunca pagou',
                        'meses_atraso': 999
                    })
            
            if inadimplentes:
                df_inad = pd.DataFrame(inadimplentes)
                st.dataframe(df_inad, use_container_width=True)
                st.warning(f"Encontrados {len(inadimplentes)} inadimplentes no período (última mensalidade há mais de {meses_verificar} meses).")
            else:
                st.success("Nenhum inadimplente encontrado (Isentos ignorados).")
                
# ==========================================
# MÓDULO 4: CONFIGURAÇÕES (CADASTRO, EDIÇÃO E EXCLUSÃO)
# ==========================================
elif modulo == "👤 Cadastro de Obreiros":
    st.subheader("Insercao de Irmaos no Quadro")
    with st.form("cad_obr"):
        n = st.text_input("Nome do Irmao")
        c = st.text_input("CIM")
        g = st.selectbox("Grau", ["Aprendiz", "Companheiro", "Mestre", "Mestre Instalado"])
        v = st.number_input("Mensalidade Fixa", value=162.0)
        isento_check = st.checkbox("Obreiro Isento de Pagamento")
        
        if st.form_submit_button("Cadastrar Obreiro"):
            # Corrigido: Incluído o campo isento e o valor convertido para inteiro (1 ou 0)
            executar_comando("INSERT INTO obreiros (nome, cim, grau, valor_mensalidade, isento) VALUES (?,?,?,?,?)", 
                             (n, c, g, v, int(isento_check)))
            st.success("Membro Cadastrado com Sucesso!")
            st.rerun()

    st.markdown("---")
    st.subheader("Gerenciar Quadro de Obreiros")
    
    # Adicionado o campo 'isento' na busca
    df_membros = buscar_dados("SELECT id, nome, cim, grau, valor_mensalidade, isento FROM obreiros ORDER BY nome")
    
    if not df_membros.empty:
        opcoes_membros = {f"{row['nome']} (CIM: {row['cim']})": row for _, row in df_membros.iterrows()}
        membro_sel = st.selectbox("Selecione um Obreiro para Editar ou Excluir:", list(opcoes_membros.keys()))
        
        dados_atuais = opcoes_membros[membro_sel]
        
        col_edit, col_excluir = st.columns(2)
        
        with col_edit:
            with st.expander(f"Editar Dados de {dados_atuais['nome']}", expanded=True):
                with st.form(f"form_edit_{dados_atuais['id']}"):
                    novo_nome = st.text_input("Nome do Irmao", value=dados_atuais['nome'])
                    novo_cim = st.text_input("CIM", value=dados_atuais['cim'])
                    novo_grau = st.selectbox("Grau", ["Aprendiz", "Companheiro", "Mestre", "Mestre Instalado"],
                                            index=["Aprendiz", "Companheiro", "Mestre", "Mestre Instalado"].index(dados_atuais['grau']))
                    novo_valor = st.number_input("Mensalidade Fixa", value=float(dados_atuais['valor_mensalidade']))
                    # Adicionado checkbox de edição com o valor salvo no banco
                    novo_isento = st.checkbox("Obreiro Isento de Pagamento", value=bool(dados_atuais['isento']))
                    
                    if st.form_submit_button("Salvar Alteracoes"):
                        # Corrigido: Incluído isento no UPDATE
                        executar_comando("""
                            UPDATE obreiros 
                            SET nome = ?, cim = ?, grau = ?, valor_mensalidade = ?, isento = ? 
                            WHERE id = ?
                        """, (novo_nome, novo_cim, novo_grau, novo_valor, int(novo_isento), int(dados_atuais['id'])))
                        st.success(f"Dados de {novo_nome} atualizados com sucesso!")
                        st.rerun()
                        
        with col_excluir:
            with st.expander("Zona de Perigo (Exclusao)", expanded=True):
                st.warning(f"Atencao: A exclusao de {dados_atuais['nome']} desvinculara suas transacoes historicas.")
                confirma_nome = st.text_input("Para confirmar, digite o CIM do obreiro:")
                
                if st.button("Excluir Obreiro Definitivamente"):
                    if confirma_nome == dados_atuais['cim']:
                        executar_comando("DELETE FROM obreiros WHERE id = ?", (int(dados_atuais['id']),))
                        st.success("Obreiro removido do quadro com sucesso.")
                        st.rerun()
                    else:
                        st.error("CIM incorreto.")
    else:
        st.info("Nenhum obreiro cadastrado.")

# ==========================================
# MÓDULO NOVO: CADASTRO DE USUÁRIOS
# ==========================================
elif modulo == "👥 Cadastro de Usuários":
    st.subheader("Gerenciamento de Usuários do Sistema")
    
    aba_cad, aba_list = st.tabs(["Cadastrar Usuário", "Listar Usuários"])
    
    with aba_cad:
        st.write("### Novo Usuário")
        with st.form("form_novo_usuario"):
            nome_usuario = st.text_input("Nome Completo")
            email_usuario = st.text_input("E-mail")
            senha_usuario = st.text_input("Senha", type="password")
            confirmar_senha = st.text_input("Confirmar Senha", type="password")
            nivel_acesso = st.selectbox("Nível de Acesso", ["usuario", "admin"])
            
            if st.form_submit_button("Cadastrar Usuário"):
                if nome_usuario and email_usuario and senha_usuario:
                    if senha_usuario == confirmar_senha:
                        # Verificar se email já existe
                        email_existe = buscar_dados("SELECT id FROM usuarios WHERE email = ?", (email_usuario,))
                        if email_existe.empty:
                            data_cadastro = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            resultado = executar_comando(
                                "INSERT INTO usuarios (nome, email, senha, nivel_acesso, data_cadastro) VALUES (?, ?, ?, ?, ?)",
                                (nome_usuario, email_usuario, senha_usuario, nivel_acesso, data_cadastro)
                            )
                            if resultado:
                                st.success("Usuário cadastrado com sucesso!")
                                st.rerun()
                        else:
                            st.error("E-mail já cadastrado no sistema.")
                    else:
                        st.error("As senhas não coincidem.")
                else:
                    st.error("Preencha todos os campos obrigatórios.")
    
    with aba_list:
        st.write("### Usuários Cadastrados")
        df_usuarios = buscar_dados("SELECT id, nome, email, nivel_acesso, ativo, data_cadastro FROM usuarios ORDER BY nome")
        
        if not df_usuarios.empty:
            df_usuarios_visual = df_usuarios.copy()
            df_usuarios_visual['ativo'] = df_usuarios_visual['ativo'].apply(lambda x: 'Sim' if x == 1 else 'Não')
            df_usuarios_visual.columns = ['ID', 'Nome', 'E-mail', 'Nível de Acesso', 'Ativo', 'Data Cadastro']
            st.dataframe(df_usuarios_visual, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            st.write("### Gerenciar Usuário")
            opcoes_usuarios = dict(zip(df_usuarios['nome'], df_usuarios['id']))
            usuario_sel = st.selectbox("Selecione um Usuário para Gerenciar:", list(opcoes_usuarios.keys()))
            
            dados_usuario = df_usuarios[df_usuarios['nome'] == usuario_sel].iloc[0]
            
            col_edit_user, col_del_user = st.columns(2)
            
            with col_edit_user:
                with st.expander(f"Editar Usuário: {dados_usuario['nome']}", expanded=True):
                    with st.form(f"form_edit_user_{dados_usuario['id']}"):
                        novo_nome_user = st.text_input("Nome", value=dados_usuario['nome'])
                        novo_email_user = st.text_input("E-mail", value=dados_usuario['email'])
                        novo_nivel_user = st.selectbox("Nível de Acesso", ["usuario", "admin"], 
                                                       index=["usuario", "admin"].index(dados_usuario['nivel_acesso']))
                        novo_ativo_user = st.checkbox("Usuário Ativo", value=bool(dados_usuario['ativo']))
                        
                        if st.form_submit_button("Salvar Alterações"):
                            executar_comando("""
                                UPDATE usuarios 
                                SET nome = ?, email = ?, nivel_acesso = ?, ativo = ? 
                                WHERE id = ?
                            """, (novo_nome_user, novo_email_user, novo_nivel_user, int(novo_ativo_user), int(dados_usuario['id'])))
                            st.success("Usuário atualizado com sucesso!")
                            st.rerun()
            
            with col_del_user:
                with st.expander("Zona de Perigo (Exclusão)", expanded=True):
                    st.warning(f"Atenção: A exclusão de {dados_usuario['nome']} é irreversível.")
                    confirma_email = st.text_input("Para confirmar, digite o e-mail do usuário:")
                    
                    if st.button("Excluir Usuário Definitivamente"):
                        if confirma_email == dados_usuario['email']:
                            executar_comando("DELETE FROM usuarios WHERE id = ?", (int(dados_usuario['id']),))
                            st.success("Usuário removido com sucesso.")
                            st.rerun()
                        else:
                            st.error("E-mail incorreto.")
        else:
            st.info("Nenhum usuário cadastrado.")

# ==========================================
# MÓDULO 5: NOTÍCIAS E INFORMAÇÕES
# ==========================================
elif modulo == "📰 Notícias e Informações":
    st.subheader("📰 Sistema de Notícias e Informações")
    
    aba_lista, aba_criar = st.tabs(["Listar Notícias", "Criar Nova Notícia"])
    
    with aba_lista:
        df_noticias = buscar_dados("SELECT * FROM noticias WHERE ativo = 1 ORDER BY data_publicacao DESC")
        
        if not df_noticias.empty:
            for index, row in df_noticias.iterrows():
                with st.expander(f"📌 {row['titulo']} - {formatar_data(row['data_publicacao'])}"):
                    st.write(f"**Autor:** {row['autor'] if row['autor'] else 'Não informado'}")
                    st.write(f"**Publicado em:** {formatar_data(row['data_publicacao'])}")
                    st.markdown("---")
                    st.write(row['conteudo'])
                    
                    col_edit, col_del = st.columns(2)
                    with col_del:
                        if st.button(f"Arquivar", key=f"del_noticia_{row['id']}"):
                            executar_comando("UPDATE noticias SET ativo = 0 WHERE id = ?", (row['id'],))
                            st.rerun()
        else:
            st.info("Nenhuma notícia publicada.")
    
    with aba_criar:
        with st.form("form_nova_noticia"):
            titulo = st.text_input("Título da Notícia")
            conteudo = st.text_area("Conteúdo", height=200)
            autor = st.text_input("Autor")
            data_pub = st.date_input("Data de Publicação", value=date.today())
            
            if st.form_submit_button("Publicar Notícia"):
                if titulo and conteudo:
                    executar_comando("""
                        INSERT INTO noticias (titulo, conteudo, data_publicacao, autor, ativo)
                        VALUES (?, ?, ?, ?, 1)
                    """, (titulo, conteudo, data_pub.strftime('%Y-%m-%d'), autor))
                    st.success("Notícia publicada com sucesso!")
                    st.rerun()
                else:
                    st.error("Preencha título e conteúdo.")

# ==========================================
# MÓDULO 6: EVENTOS E AGENDA
# ==========================================
elif modulo == "📅 Eventos e Agenda":
    st.subheader("📅 Eventos e Agenda da Loja")
    
    aba_eventos, aba_criar_evento = st.tabs(["Calendário de Eventos", "Criar Evento"])
    
    with aba_eventos:
        df_eventos = buscar_dados("SELECT * FROM eventos ORDER BY data_evento ASC")
        
        if not df_eventos.empty:
            for index, row in df_eventos.iterrows():
                with st.expander(f"🗓️ {row['titulo']} - {formatar_data(row['data_evento'])}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Data:** {formatar_data(row['data_evento'])}")
                        st.write(f"**Hora:** {row['hora'] if row['hora'] else 'Não informado'}")
                    with col2:
                        st.write(f"**Local:** {row['local'] if row['local'] else 'Não informado'}")
                        st.write(f"**Tipo:** {row['tipo']}")
                    
                    if row['descricao']:
                        st.markdown("---")
                        st.write(row['descricao'])
                    
                    if st.button(f"Excluir Evento", key=f"del_evento_{row['id']}"):
                        executar_comando("DELETE FROM eventos WHERE id = ?", (row['id'],))
                        st.rerun()
        else:
            st.info("Nenhum evento agendado.")
    
    with aba_criar_evento:
        with st.form("form_novo_evento"):
            titulo = st.text_input("Título do Evento")
            descricao = st.text_area("Descrição", height=100)
            data_evento = st.date_input("Data do Evento")
            hora = st.time_input("Horário")
            local = st.text_input("Local")
            tipo = st.selectbox("Tipo de Evento", ["Geral", "Reunião Administrativa", "Cerimônia", "Instrução", "Social"])
            
            if st.form_submit_button("Agendar Evento"):
                if titulo and data_evento:
                    executar_comando("""
                        INSERT INTO eventos (titulo, descricao, data_evento, hora, local, tipo)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (titulo, descricao, data_evento.strftime('%Y-%m-%d'), hora.strftime('%H:%M'), local, tipo))
                    st.success("Evento agendado com sucesso!")
                    st.rerun()
                else:
                    st.error("Preencha título e data do evento.")

# ==========================================
# MÓDULO 7: ANIVERSARIANTES
# ==========================================
elif modulo == "🎂 Aniversariantes":
    st.subheader("🎂 Aniversariantes do Mês")
    
    mes_atual = st.selectbox("Selecione o Mês", MESES, index=date.today().month - 1)
    mes_numero = MESES.index(mes_atual) + 1
    
    # Buscar aniversariantes do mês
    query = """
        SELECT nome, data_nascimento, cim, grau 
        FROM obreiros 
        WHERE strftime('%m', data_nascimento) = ?
        ORDER BY strftime('%d', data_nascimento) ASC
    """
    
    df_aniversariantes = buscar_dados(query, (f"{mes_numero:02d}",))
    
    if not df_aniversariantes.empty:
        st.success(f"Encontrados {len(df_aniversariantes)} aniversariantes em {mes_atual}")
        
        for index, row in df_aniversariantes.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 2])
                with col1:
                    st.write(f"**{row['nome']}**")
                with col2:
                    st.write(f"CIM: {row['cim']}")
                with col3:
                    st.write(f"Grau: {row['grau']}")
                
                if row['data_nascimento']:
                    try:
                        data_nasc = datetime.strptime(row['data_nascimento'], '%Y-%m-%d')
                        hoje = date.today()
                        idade = hoje.year - data_nasc.year
                        if (hoje.month, hoje.day) < (data_nasc.month, data_nasc.day):
                            idade -= 1
                        st.write(f"📅 {formatar_data(row['data_nascimento'])} - {idade} anos")
                    except:
                        st.write(f"📅 {formatar_data(row['data_nascimento'])}")
                
                st.markdown("---")
    else:
        st.info(f"Nenhum aniversariante encontrado em {mes_atual}.")
    
    st.markdown("---")
    st.subheader("Adicionar Data de Nascimento")
    
    df_obs = buscar_dados("SELECT id, nome, cim, data_nascimento FROM obreiros ORDER BY nome")
    
    if not df_obs.empty:
        obreiro_sel = st.selectbox("Selecione o Obreiro", df_obs['nome'].tolist())
        
        if obreiro_sel:
            obreiro_data = df_obs[df_obs['nome'] == obreiro_sel].iloc[0]
            
            with st.form("form_data_nascimento"):
                valor_padrao = date.today()
                if obreiro_data['data_nascimento']:
                    try:
                        valor_padrao = datetime.strptime(obreiro_data['data_nascimento'], '%Y-%m-%d').date()
                    except:
                        pass
                data_nasc = st.date_input("Data de Nascimento", value=valor_padrao)
                
                if st.form_submit_button("Salvar Data de Nascimento"):
                    executar_comando("UPDATE obreiros SET data_nascimento = ? WHERE id = ?", 
                                   (data_nasc.strftime('%Y-%m-%d'), obreiro_data['id']))
                    st.success("Data de nascimento atualizada!")
                    st.rerun()
    else:
        st.info("Nenhum obreiro cadastrado.")

# ==========================================
# MÓDULO 8: BACKUP E RESTAURAÇÃO
# ==========================================
elif modulo == "💾 Backup e Restauração":
    st.subheader("💾 Backup e Restauração do Banco de Dados")
    
    aba_backup, aba_restaurar = st.tabs(["📥 Fazer Backup", "📤 Restaurar Backup"])
    
    with aba_backup:
        st.write("### Fazer Backup do Banco de Dados")
        st.info("Esta opção permite baixar uma cópia completa do banco de dados.")
        
        try:
            with open(DB_PATH, 'rb') as f:
                db_bytes = f.read()
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            st.download_button(
                label="📥 Baixar Backup",
                data=db_bytes,
                file_name=f"financas_loja_backup_{timestamp}.db",
                mime="application/x-sqlite3",
                use_container_width=True
            )
            
            st.success(f"Tamanho do backup: {len(db_bytes) / 1024:.2f} KB")
        except Exception as e:
            st.error(f"Erro ao criar backup: {str(e)}")
    
    with aba_restaurar:
        st.write("### Restaurar Backup do Banco de Dados")
        st.warning("⚠️ **ATENÇÃO**: A restauração substituirá todos os dados atuais pelo backup selecionado. Esta ação não pode ser desfeita!")
        
        arquivo_backup = st.file_uploader(
            "Selecione o arquivo de backup (.db)",
            type=['db'],
            help="Selecione um arquivo de backup do banco de dados SQLite"
        )
        
        if arquivo_backup:
            st.info(f"Arquivo selecionado: {arquivo_backup.name} ({arquivo_backup.size / 1024:.2f} KB)")
            
            col_conf1, col_conf2 = st.columns(2)
            with col_conf1:
                confirmar_nome = st.text_input("Digite 'CONFIRMAR' para autorizar a restauração:", placeholder="CONFIRMAR")
            with col_conf2:
                confirmar = st.checkbox("Entendo que todos os dados atuais serão perdidos")
            
            if st.button("📤 Restaurar Backup", use_container_width=True, type="primary"):
                if confirmar_nome.upper() == "CONFIRMAR" and confirmar:
                    try:
                        # Criar backup de segurança antes de restaurar
                        backup_seguranca = f"{DB_PATH}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        import shutil
                        shutil.copy2(DB_PATH, backup_seguranca)
                        
                        # Restaurar o backup
                        with open(DB_PATH, 'wb') as f:
                            f.write(arquivo_backup.getvalue())
                        
                        st.success(f"✅ Backup restaurado com sucesso!")
                        st.info(f"📁 Backup de segurança salvo em: {backup_seguranca}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erro ao restaurar backup: {str(e)}")
                else:
                    st.error("❌ Você deve digitar 'CONFIRMAR' e marcar a checkbox para prosseguir.")
        else:
            st.info("Nenhum arquivo selecionado.")