# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime
import plotly.express as px
from fpdf import FPDF

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA E DESIGN MAÇÔNICO
# ==========================================
st.set_page_config(page_title="Tesouraria - Jeronimo Rosado 1994", layout="wide")

st.markdown("""
    <style>
    /* Força cores sólidas em qualquer tema */
    div[data-testid="stMetricValue"] {
        color: #1e293b !important;
        background-color: #f1f5f9;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
    }
    /* Cores de status fixas */
    .metric-receita { color: #166534 !important; }
    .metric-despesa { color: #991b1b !important; }
    .metric-saldo { color: #1e40af !important; }
    
    /* Melhoria na Tabela */
    .stDataFrame { border: 1px solid #e2e8f0; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CONFIGURAÇÃO DO BANCO DE DADOS (MYSQL)
# ==========================================
DB_CONFIG = {
    'host': 'localhost',         
    'user': 'rodrigo',       
    'password': '12345', 
    'database': 'financas',      
    'charset': 'utf8mb4'         
}

def init_db():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS obreiros (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            cim VARCHAR(50) DEFAULT '000000',
            grau VARCHAR(100) NOT NULL,
            valor_mensalidade DECIMAL(10,2) NOT NULL,
            status_isento TINYINT DEFAULT 0,
            data_admissao DATE DEFAULT '2026-01-01'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transacoes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            data DATE NOT NULL,
            tipo VARCHAR(50) NOT NULL,
            categoria VARCHAR(100) NOT NULL,
            descricao TEXT NOT NULL,
            valor DECIMAL(10,2) NOT NULL,
            obreiro_id INT,
            mes_competencia VARCHAR(50),
            ano_competencia VARCHAR(50),
            FOREIGN KEY (obreiro_id) REFERENCES obreiros(id) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    
    cursor.execute("SELECT COUNT(*) FROM obreiros")
    if cursor.fetchone()[0] == 0:
        query_ins = """
            INSERT INTO obreiros (nome, cim, grau, valor_mensalidade, status_isento, data_admissao) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        valores = [
            ("Agenilton Goncalves de Lima", "336627", "Mestre", 162.00, 0, "2026-01-01"),
            ("Raimundo Nonato", "123456", "Mestre", 100.00, 0, "2026-01-01"),
            ("Antonio da Silva", "789101", "Companheiro", 100.00, 0, "2026-01-01")
        ]
        cursor.executemany(query_ins, valores)
        
    conn.commit()
    cursor.close()
    conn.close()

init_db()

def buscar_dados(query, params=()):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    query = query.replace('?', '%s')
    cursor.execute(query, params)
    resultados = cursor.fetchall()
    cursor.close()
    conn.close()
    return pd.DataFrame(resultados)

def executar_comando(query, params=()):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    query = query.replace('?', '%s')
    cursor.execute(query, params)
    conn.commit()
    cursor.close()
    conn.close()

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
    
    
    meses_lista = ["Janeiro", "Fevereiro", "Marco", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
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
    
    for _, trans in df_trans.iterrows():
        cat = trans['categoria']
        if "Mensalidade" in cat: cat_key = "Mensalidade Loja"
        elif "PAF" in cat or "Funeral" in cat: cat_key = "Auxilio Funeral (PAF)"
        elif "Federal" in cat: cat_key = "Anuidade GOB Federal"
        elif "RN" in cat: cat_key = "Anuidade GOB RN"
        elif "Feminina" in cat: cat_key = "Fraternidade Feminina"
        else: cat_key = "Taxa Extra"
        
        if cat_key in matriz and trans['mes_competencia'] in meses_lista:
            matriz[cat_key][trans['mes_competencia']] += float(trans['valor'])
            
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
            val_str = f"{val:,.2f}".replace(".", ",").replace(",00", "") if val > 0 else "-"
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
    pdf.cell(0, 5, "Oriente de Mossoro - RN | GOB-RN | Sistema de Secretaria Integrado", ln=True, align='C')
    
    pdf.ln(2)
    pdf.set_text_color(212, 175, 55)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 6, "T.F.A.", ln=True, align='C')
    
    return bytes(pdf.output())

# ==========================================
# INTERFACE E NAVEGAÇÃO DO STREAMLIT
# ==========================================
st.sidebar.header("Menu de Navegacao")
modulo = st.sidebar.radio("Selecione o Modulo:", [
    "Painel de Controle (Dashboard)", 
    "Livro Caixa (Lancar e Editar)",
    "Gerenciar Categorias", 
    "Carteira de Obreiros (Mensalidades)",
    "Cadastro de Obreiros"
    
])

MESES = ["Janeiro", "Fevereiro", "Marco", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
ANOS = ["2026", "2027", "2028"]

# ==========================================
# MÓDULO 1: DASHBOARD FINANCEIRO REALTIME
# ==========================================
if modulo == "Painel de Controle (Dashboard)":
    st.subheader("Demonstrativo de Resultados Financeiros Integrado")
    
    st.write("### Filtros do Periodo")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        ano_sel = st.selectbox("Selecione o Ano para Analise:", ANOS)
    with col_f2:
        mes_sel = st.selectbox("Selecione o Mes para Analise:", ["Ano Completo"] + MESES)
    
    if mes_sel == "Ano Completo":
        query_dash = """
            SELECT data, tipo, categoria, descricao, valor, mes_competencia 
            FROM transacoes 
            WHERE YEAR(data) = ? OR ano_competencia = ?
        """
        params_dash = (int(ano_sel), ano_sel)
    else:
        query_dash = """
            SELECT data, tipo, categoria, descricao, valor, mes_competencia 
            FROM transacoes 
            WHERE (YEAR(data) = ? OR ano_competencia = ?) AND mes_competencia = ?
        """
        params_dash = (int(ano_sel), ano_sel, mes_sel)
        
    df_dash = buscar_dados(query_dash, params_dash)
    total_obreiros_cad = len(buscar_dados("SELECT id FROM obreiros"))
    
    if not df_dash.empty:
        df_dash['valor'] = pd.to_numeric(df_dash['valor'], errors='coerce').fillna(0.0)
        df_dash['tipo'] = df_dash['tipo'].astype(str).str.strip().str.replace('Saída', 'Saida')
        
        ent = float(df_dash[df_dash['tipo'] == 'Entrada']['valor'].sum())
        sai = float(df_dash[df_dash['tipo'].isin(['Saída', 'Saida'])]['valor'].sum())
        saldo = ent - sai
        
        if mes_sel != "Ano Completo":
            obr_ativos_no_mes = df_dash[(df_dash['tipo'] == 'Entrada') & (df_dash['categoria'] == 'Mensalidade Loja')]['mes_competencia'].count()
            inadimplentes = max(0, total_obreiros_cad - obr_ativos_no_mes)
        else:
            inadimplentes = 0
            
        st.markdown("---")
        
        # Injeção de CSS Dinâmico para colorir individualmente cada card de métrica
        # CSS de alta prioridade para garantir visibilidade em qualquer tema
        st.markdown("""
            <style>
            /* Forca a cor do texto das métricas, ignorando o tema automático */
            [data-testid="stMetricValue"] {
                color: #1e293b !important; /* Cinza muito escuro, quase preto, para legibilidade */
            }

            /* Especificidade para cada coluna */
            div[data-testid="column"]:nth-of-type(1) [data-testid="stMetricValue"] { color: #22c55e !important; } /* Verde */
            div[data-testid="column"]:nth-of-type(2) [data-testid="stMetricValue"] { color: #ef4444 !important; } /* Vermelho */
            div[data-testid="column"]:nth-of-type(3) [data-testid="stMetricValue"] { color: #3b82f6 !important; } /* Azul */
            
            /* Ajuste para o card de Inadimplência (Preto) */
            div[data-testid="column"]:nth-of-type(4) [data-testid="stMetricValue"] { 
                color: #000000 !important; 
                font-weight: 800 !important;
            }
            
            /* Ajuste dos labels para garantir que nao fiquem invisiveis */
            [data-testid="stMetricLabel"] {
                color: #64748b !important;
            }
            </style>
        """, unsafe_allow_html=True)
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Receitas (Entradas)", f"R$ {ent:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        c2.metric("Despesas (Saidas)", f"R$ {sai:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        
        if saldo >= 0:
            c3.metric("Saldo Liquido", f"R$ {saldo:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        else:
            c3.metric("Saldo Liquido (Deficit)", f"R$ {saldo:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            
        if mes_sel != "Ano Completo":
            c4.metric("Inadimplencia Estimada", f"{inadimplentes} Obreiros", delta=f"Cadastrados: {total_obreiros_cad}", delta_color="off")
        else:
            c4.metric("Inadimplencia Estimada", "N/A", help="Selecione um mes especifico para auditar a adimplencia.")
            
        st.markdown("---")
        st.subheader(f"Distribucao Financeira - {mes_sel} / {ano_sel}")
        
        col_g1, col_g2 = st.columns([1, 1])
        
        with col_g1:
            st.write("**Proporcao de Caixa (Entradas vs Saidas)**")
            resumo_tipo = df_dash.groupby('tipo', as_index=False)['valor'].sum()
            fig_pizza = px.pie(resumo_tipo, values='valor', names='tipo', hole=0.4,
                               color='tipo', color_discrete_map={'Entrada':'#22c55e', 'Saida':'#ef4444', 'Saída':'#ef4444'})
            fig_pizza.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                                    font=dict(color='#94a3b8'), margin=dict(t=20, b=20, l=0, r=0))
            st.plotly_chart(fig_pizza, use_container_width=True)
            
        with col_g2:
            st.write("**Gastos e Destinacoes por Categoria**")
            df_saidas = df_dash[df_dash['tipo'].isin(['Saída', 'Saida'])]
            if not df_saidas.empty:
                resumo_cat = df_saidas.groupby('categoria', as_index=False)['valor'].sum().sort_values(by='valor', ascending=True)
                fig_barra = px.bar(resumo_cat, x='valor', y='categoria', orientation='h', color_discrete_sequence=['#d4af37'])
                fig_barra.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                        xaxis_title="Total (R$)", yaxis_title="",
                                        font=dict(color='#94a3b8'), margin=dict(t=20, b=20, l=0, r=0))
                st.plotly_chart(fig_barra, use_container_width=True)
            else:
                st.info("Nenhuma despesa ou saida registrada neste periodo para gerar o grafico.")
                
        st.markdown("---")
        st.subheader("Livro de Lancamentos do Periodo Filtrado")
        
        df_tabela = df_dash.copy()
        df_tabela['valor_formatado'] = df_tabela['valor'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        
        st.dataframe(
            df_tabela[['data', 'tipo', 'categoria', 'descricao', 'valor_formatado']], 
            use_container_width=True, 
            hide_index=True
        )
        
        st.write("### Exportar Balancete")
        df_export = df_dash[['data', 'tipo', 'categoria', 'descricao', 'valor']].copy()
        csv_data = df_export.to_csv(index=False, sep=';', encoding='utf-8-sig')
        
        st.download_button(
            label="Baixar Relatorio Balancete (CSV/Excel)",
            data=csv_data,
            file_name=f"Balancete_{mes_sel.replace(' ', '_')}_{ano_sel}.csv",
            mime="text/csv",
            key="btn_export_dash"
        )
    else:
        st.info(f"Nenhum registro financeiro encontrado para o periodo de {mes_sel} de {ano_sel}.")

elif modulo == "Gerenciar Categorias":
    st.subheader("Configuracao de Categorias")
    
    # Cadastro de nova categoria
    with st.form("form_nova_cat"):
        nome_cat = st.text_input("Nome da nova categoria:")
        if st.form_submit_button("Cadastrar Categoria"):
            if nome_cat.strip() != "":
                executar_comando("INSERT IGNORE INTO categorias (nome) VALUES (?)", (nome_cat,))
                st.success("Categoria cadastrada!")
                st.rerun()
    
    # Listagem e Exclusão
    df_cats = buscar_dados("SELECT id, nome FROM categorias ORDER BY nome")
    if not df_cats.empty:
        st.write("### Categorias Existentes")
        for index, row in df_cats.iterrows():
            col1, col2 = st.columns([3, 1])
            col1.write(row['nome'])
            if col2.button("Excluir", key=f"del_{row['id']}"):
                executar_comando("DELETE FROM categorias WHERE id = ?", (row['id'],))
                st.rerun()
    else:
        st.info("Nenhuma categoria cadastrada.")
        
elif modulo == "Livro Caixa (Lancar e Editar)":
    st.subheader("Lancamentos no Livro do Caixa")
    
    # Busca categorias do banco
    df_cats = buscar_dados("SELECT nome FROM categorias ORDER BY nome")
    lista_cats = df_cats['nome'].tolist() if not df_cats.empty else ["Outros"]

    with st.form("form_caixa"):
        dat = st.date_input("Data")
        tip = st.selectbox("Tipo", ["Saída", "Entrada"])
        cat = st.selectbox("Categoria", lista_cats)
        desc = st.text_input("Descricao / Credor")
        val = st.number_input("Valor", min_value=0.0)
        
        if st.form_submit_button("Lancar"):
            executar_comando("INSERT INTO transacoes (data, tipo, categoria, descricao, valor, mes_competencia, ano_competencia) VALUES (?,?,?,?,?,?,?)",
                             (dat.strftime('%Y-%m-%d'), tip, cat, desc, val, dat.strftime('%B'), dat.strftime('%Y')))
            st.success("Lancado!")
            st.rerun()

    st.markdown("---")
    st.subheader("Historico de Lancamentos Recentes")
    
    df_lista_trans = buscar_dados("SELECT id, data, tipo, categoria, descricao, valor FROM transacoes ORDER BY id DESC")
    
    if not df_lista_trans.empty:
        df_visualizacao = df_lista_trans.copy()
        df_visualizacao['valor'] = df_visualizacao['valor'].apply(lambda x: f"R$ {float(x):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        
        st.dataframe(df_visualizacao, use_container_width=True, hide_index=True)
        
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
# MÓDULO 3: CARTEIRA DE OBREIROS & RELATÓRIO DE INADIMPLÊNCIA
# ==========================================
elif modulo == "Carteira de Obreiros (Mensalidades)":
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
            
            # Verificacao de duplicidade
            ja_lancado = buscar_dados("SELECT id FROM transacoes WHERE obreiro_id = ? AND mes_competencia = ? AND ano_competencia = ? AND categoria = 'Mensalidade Loja'", (id_irmao, mes_b, ano_b))
            processar = True
            if not ja_lancado.empty:
                st.warning("Este mes ja foi lancado para este obreiro.")
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
                            executar_comando("INSERT INTO transacoes (data, tipo, categoria, valor, obreiro_id, mes_competencia, ano_competencia) VALUES (CURDATE(), 'Entrada', ?, ?, ?, ?, ?)", 
                                             (cat, val, id_irmao, mes_b, ano_b))
                    st.success("Lancamento efetuado com sucesso.")
                    st.rerun()

    with aba_inad:
        st.write("### Auditoria de Inadimplencia")
        periodo_sel = st.selectbox("Filtrar por:", ["Ultimos 3 meses", "Ultimos 6 meses", "1 ano"])
        
        if st.button("Gerar Relatorio de Inadimplencia"):
            dias = 90 if "3 meses" in periodo_sel else (180 if "6 meses" in periodo_sel else 365)
            
            # A nova query adiciona a condição: AND isento = 0
            query = f"""
                SELECT nome, cim 
                FROM obreiros 
                WHERE id NOT IN (
                    SELECT DISTINCT obreiro_id FROM transacoes 
                    WHERE categoria = 'Mensalidade Loja' 
                    AND data >= DATE_SUB(CURDATE(), INTERVAL {dias} DAY)
                )
                AND isento = 0
            """
            
            df_inad = buscar_dados(query)
            
            if not df_inad.empty:
                st.dataframe(df_inad, use_container_width=True)
            else:
                st.success("Nenhum inadimplente encontrado (Isentos ignorados).")
                
# ==========================================
# MÓDULO 4: CONFIGURAÇÕES (CADASTRO, EDIÇÃO E EXCLUSÃO)
# ==========================================
elif modulo == "Cadastro de Obreiros":
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