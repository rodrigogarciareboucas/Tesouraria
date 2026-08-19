import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA E DESIGN (MAÇÔNICO)
# ==========================================
st.set_page_config(page_title="Tesouraria - Jerônimo Rosado 1994", page_icon="🏛️", layout="wide")

# Customização de cores para manter a identidade Azul-Escuro e Dourado
st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #f8fafc; }
    h1, h2, h3 { color: #d4af37 !important; font-family: 'Poppins', sans-serif; }
    .stButton>button { background-color: #d4af37; color: #001f3f; font-weight: bold; border-radius: 5px; }
    .stButton>button:hover { background-color: #001f3f; color: #d4af37; border: 1px solid #d4af37; }
    div[data-testid="stMetricValue"] { color: #ffffff !important; }
    div[data-testid="stMetricLabel"] { color: #94a3b8 !important; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. INICIALIZAÇÃO DO BANCO DE DADOS (SQLITE)
# ==========================================
def init_db():
    conn = sqlite3.connect('financas_loja.db')
    cursor = conn.cursor()
    
    # Tabela de Obreiros
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS obreiros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            grau TEXT NOT NULL,
            valor_mensalidade REAL NOT NULL,
            status_isento INTEGER DEFAULT 0,
            data_cadastro TEXT DEFAULT CURRENT_DATE
        )
    """)
    
    # Tabela de Fluxo de Caixa (Transações)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            tipo TEXT NOT NULL, -- 'Entrada' ou 'Saída'
            categoria TEXT NOT NULL,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            obreiro_id INTEGER,
            data_cadastro TEXT DEFAULT CURRENT_DATE,
            FOREIGN KEY (obreiro_id) REFERENCES obreiros(id)
        )
    """)
    
    # Criar índices para melhorar performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_transacoes_data ON transacoes(data)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_transacoes_tipo ON transacoes(tipo)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_transacoes_categoria ON transacoes(categoria)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_transacoes_obreiro ON transacoes(obreiro_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_obreiros_nome ON obreiros(nome)")
    
    # Inserir dados fictícios de obreiros para demonstração caso esteja vazio
    cursor.execute("SELECT COUNT(*) FROM obreiros")
    if cursor.fetchone()[0] == 0:
        obreiros_dados = [
            ("Raimundo Nonato", "Mestre", 100.00, 0, '2025-01-01'),
            ("Antônio da Silva", "Companheiro", 100.00, 0, '2025-01-01'),
            ("Francisco José", "Aprendiz", 100.00, 0, '2025-01-01'),
            ("José de Alencar", "Mestre Instalado", 100.00, 0, '2025-01-01'),
            ("Manoel Rodrigues", "Mestre", 0.00, 1, '2025-01-01') # Isento
        ]
        cursor.executemany("INSERT INTO obreiros (nome, grau, valor_mensalidade, status_isento, data_cadastro) VALUES (?, ?, ?, ?, ?)", obreiros_dados)
        
        # Inserir algumas transações históricas baseadas nos seus extratos reais
        transacoes_dados = [
            ('2026-03-02', 'Saída', 'GOB RN', 'Taxa Mensal GOB RN', 450.00, None),
            ('2026-03-05', 'Saída', 'Energia', 'Neoenergia Cosern Fatura Templo', 1655.83, None),
            ('2026-03-10', 'Saída', 'IPTU / Taxas', 'Prefeitura de Mossoró', 964.33, None),
            ('2026-03-11', 'Saída', 'GOB Federal', 'Capitação GOB', 1691.33, None),
            ('2026-03-20', 'Saída', 'GOB Federal', 'Capitação GOB (PIX)', 1691.33, None),
            ('2026-05-15', 'Entrada', 'Tronco de Beneficência', 'Coleta Sessão Ordinária', 350.00, None),
            ('2026-05-10', 'Entrada', 'Mensalidade', 'Mensalidade Março - Raimundo Nonato', 100.00, 1),
            ('2026-05-10', 'Entrada', 'Mensalidade', 'Mensalidade Março - Antônio da Silva', 100.00, 2),
            ('2026-05-19', 'Entrada', 'Eventos', 'Inscrições Dia das Mães (46 ord.)', 2300.00, None),
            ('2026-05-19', 'Saída', 'Eventos', 'Despesas Insumos Dia das Mães', 1481.56, None)
        ]
        cursor.executemany("INSERT INTO transacoes (data, tipo, categoria, descricao, valor, obreiro_id) VALUES (?, ?, ?, ?, ?, ?)", transacoes_dados)
        
    conn.commit()
    conn.close()

init_db()

# Funções auxiliares de banco
def buscar_dados(query, params=()):
    try:
        conn = sqlite3.connect('financas_loja.db')
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Erro ao buscar dados: {str(e)}")
        return pd.DataFrame()

def executar_comando(query, params=()):
    try:
        conn = sqlite3.connect('financas_loja.db')
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
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
    return data_str

# ==========================================
# 3. INTERFACE E NAVEGAÇÃO DO STREAMLIT
# ==========================================
st.title("🏛️ Sistema de Gestão Financeira — Loja Jerônimo Rosado 1994")
st.markdown("---")

menu = ["Visão Geral (Dashboard)", "Lançar Transação", "Controle de Obreiros", "Cadastrar Irmão", "Relatórios Financeiros"]
escolha = st.sidebar.selectbox("Módulos do Sistema", menu)

# ==========================================
# MÓDULO 1: VISÃO GERAL (DASHBOARD)
# ==========================================
if escolha == "Visão Geral (Dashboard)":
    st.subheader("📊 Painel Financeiro Consolidado")
    
    # Filtros de período
    col_filtro1, col_filtro2 = st.columns(2)
    with col_filtro1:
        data_inicio = st.date_input("Data Início", value=date(2026, 1, 1))
    with col_filtro2:
        data_fim = st.date_input("Data Fim", value=date.today())
    
    # Cálculo de Métricas Globais com filtro
    df_transacoes = buscar_dados("SELECT * FROM transacoes WHERE data BETWEEN ? AND ?", 
                                (data_inicio.strftime('%Y-%m-%d'), data_fim.strftime('%Y-%m-%d')))
    df_transacoes['valor'] = df_transacoes['valor'].astype(float)
    df_transacoes['data'] = pd.to_datetime(df_transacoes['data'])
    
    total_entradas = df_transacoes[df_transacoes['tipo'] == 'Entrada']['valor'].sum()
    total_saidas = df_transacoes[df_transacoes['tipo'] == 'Saída']['valor'].sum()
    saldo_caixa = total_entradas - total_saidas
    
    # Cards de KPI
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de Entradas", formatar_moeda(total_entradas))
    col2.metric("Total de Saídas", formatar_moeda(total_saidas))
    col3.metric("Saldo Líquido", formatar_moeda(saldo_caixa), 
                delta=formatar_moeda(saldo_caixa), delta_color="normal" if saldo_caixa >= 0 else "inverse")
    
    # Transações no período
    total_transacoes = len(df_transacoes)
    col4.metric("Transações", f"{total_transacoes}")
    
    st.markdown("---")
    
    # Gráficos
    col_graf1, col_graf2 = st.columns(2)
    
    with col_graf1:
        st.subheader("📈 Receitas x Despesas")
        df_tipo = df_transacoes.groupby('tipo')['valor'].sum().reset_index()
        fig_tipo = px.pie(df_tipo, values='valor', names='tipo', 
                          color_discrete_map={'Entrada': '#22c55e', 'Saída': '#ef4444'},
                          hole=0.4)
        fig_tipo.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_tipo, use_container_width=True)
    
    with col_graf2:
        st.subheader("📊 Despesas por Categoria")
        df_saidas = df_transacoes[df_transacoes['tipo'] == 'Saída']
        if not df_saidas.empty:
            df_categoria = df_saidas.groupby('categoria')['valor'].sum().reset_index()
            df_categoria = df_categoria.sort_values('valor', ascending=True)
            fig_categoria = px.bar(df_categoria, x='valor', y='categoria', 
                                  orientation='h', color='valor',
                                  color_continuous_scale='Reds')
            fig_categoria.update_layout(xaxis_title="Valor (R$)", yaxis_title="")
            st.plotly_chart(fig_categoria, use_container_width=True)
        else:
            st.info("Não há despesas no período selecionado")
    
    st.markdown("---")
    
    # Evolução mensal
    st.subheader("📅 Evolução Mensal")
    df_transacoes['mes_ano'] = df_transacoes['data'].dt.to_period('M')
    df_mensal = df_transacoes.groupby(['mes_ano', 'tipo'])['valor'].sum().reset_index()
    df_mensal['mes_ano'] = df_mensal['mes_ano'].astype(str)
    
    fig_evolucao = px.line(df_mensal, x='mes_ano', y='valor', color='tipo',
                          color_discrete_map={'Entrada': '#22c55e', 'Saída': '#ef4444'},
                          markers=True)
    fig_evolucao.update_layout(xaxis_title="Mês/Ano", yaxis_title="Valor (R$)")
    st.plotly_chart(fig_evolucao, use_container_width=True)
    
    st.markdown("---")
    
    # Filtro e visualização do Livro Caixa
    st.subheader("📜 Extrato Detalhado (Livro Caixa)")
    df_exibicao = df_transacoes.sort_values(by="data", ascending=False).copy()
    df_exibicao['data'] = df_exibicao['data'].dt.strftime('%d/%m/%Y')
    
    # Formatação amigável para exibição
    df_exibicao.columns = ["ID", "Data", "Tipo", "Categoria", "Descrição / Favorecido", "Valor (R$)", "ID Obreiro", "Data Cadastro"]
    st.dataframe(df_exibicao[["Data", "Tipo", "Categoria", "Descrição / Favorecido", "Valor (R$)"]], 
                use_container_width=True, height=400)

# ==========================================
# MÓDULO 2: LANÇAR TRANSAÇÃO
# ==========================================
elif escolha == "Lançar Transação":
    st.subheader("✍️ Registrar Novo Lançamento Financeiro")
    
    tipo = st.radio("Tipo de Transação", ["Entrada", "Saída"], horizontal=True)
    
    col1, col2 = st.columns(2)
    with col1:
        data = st.date_input("Data da Operação", datetime.today())
        valor = st.number_input("Valor da Transação (R$)", min_value=0.01, step=10.0)
    
    with col2:
        if tipo == "Entrada":
            categoria = st.selectbox("Categoria de Entrada", ["Mensalidade", "Tronco de Beneficência", "Iniciação/Elevação/Exaltação", "Doação", "Eventos"])
        else:
            categoria = st.selectbox("Categoria de Saída", ["GOB Federal", "GOB RN", "Energia", "IPTU / Taxas", "Internet / Comunicação", "Manutenção do Templo", "Eventos", "Beneficência / Hospitalaria"])
            
        descricao = st.text_input("Descrição Detalhada / Favorecido")
        
    # Se for pagamento de mensalidade, vincula ao irmão
    obreiro_id = None
    if tipo == "Entrada" and categoria == "Mensalidade":
        df_obs = buscar_dados("SELECT id, nome FROM obreiros WHERE status_isento = 0")
        lista_obreiros = dict(zip(df_obs['nome'], df_obs['id']))
        obreiro_selecionado = st.selectbox("Vincular ao Irmão:", list(lista_obreiros.keys()))
        if obreiro_selecionado:
            obreiro_id = int(lista_obreiros[obreiro_selecionado])
            
    if st.button("Salvar Lançamento no Banco"):
        executar_comando("""
            INSERT INTO transacoes (data, tipo, categoria, descricao, valor, obreiro_id) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (data.strftime('%Y-%m-%d'), tipo, categoria, descricao, valor, obreiro_id))
        st.success(f"Sucesso! {tipo} de R$ {valor:.2f} registrada com êxito.")
    
    st.markdown("---")
    st.subheader("🔧 Gerenciar Transações Recentes")
    
    # Listar últimas transações para edição/exclusão
    df_ultimas_transacoes = buscar_dados("SELECT * FROM transacoes ORDER BY data DESC LIMIT 10")
    if not df_ultimas_transacoes.empty:
        df_ultimas_transacoes['data'] = pd.to_datetime(df_ultimas_transacoes['data']).dt.strftime('%d/%m/%Y')
        st.dataframe(df_ultimas_transacoes[['id', 'data', 'tipo', 'categoria', 'descricao', 'valor']], 
                    use_container_width=True)
        
        transacao_id_edit = st.number_input("ID da Transação para Editar/Excluir:", min_value=1, step=1)
        
        if transacao_id_edit:
            transacao_dados = buscar_dados("SELECT * FROM transacoes WHERE id = ?", (transacao_id_edit,))
            if not transacao_dados.empty:
                transacao_dados = transacao_dados.iloc[0]
                
                col_trans1, col_trans2 = st.columns(2)
                with col_trans1:
                    edit_data = st.date_input("Nova Data", value=pd.to_datetime(transacao_dados['data']).to_pydatetime())
                    edit_valor = st.number_input("Novo Valor", min_value=0.01, value=float(transacao_dados['valor']))
                with col_trans2:
                    edit_categoria = st.text_input("Nova Categoria", value=transacao_dados['categoria'])
                    edit_descricao = st.text_input("Nova Descrição", value=transacao_dados['descricao'])
                
                col_btn_trans1, col_btn_trans2 = st.columns(2)
                with col_btn_trans1:
                    if st.button("Atualizar Transação"):
                        executar_comando("""
                            UPDATE transacoes SET data = ?, valor = ?, categoria = ?, descricao = ? WHERE id = ?
                        """, (edit_data.strftime('%Y-%m-%d'), edit_valor, edit_categoria, edit_descricao, transacao_id_edit))
                        st.success("Transação atualizada com sucesso!")
                        st.rerun()
                
                with col_btn_trans2:
                    if st.button("Excluir Transação", type="secondary"):
                        executar_comando("DELETE FROM transacoes WHERE id = ?", (transacao_id_edit,))
                        st.success("Transação excluída com sucesso!")
                        st.rerun()
            else:
                st.warning("Transação não encontrada.")

# ==========================================
# MÓDULO 3: CONTROLE DE OBREIROS (SITUAÇÃO FINANCEIRA)
# ==========================================
elif escolha == "Controle de Obreiros":
    st.subheader("👥 Quadro de Obreiros e Situação de Metais")
    
    # Buscar lista de obreiros e pagamentos de mensalidade recentes
    df_obreiros = buscar_dados("SELECT * FROM obreiros")
    
    # Lógica aprimorada de conferência de inadimplência com cálculo por data real
    data_atual = datetime.now()
    ano_atual = data_atual.year
    mes_atual = data_atual.month
    
    situacao_dados = []
    for idx, row in df_obreiros.iterrows():
        if row['status_isento'] == 1:
            sit = "Isento / Remido"
            devido = 0.0
        else:
            # Verifica mensalidades pagas no ano atual
            pagamentos_ano = buscar_dados(
                "SELECT COUNT(*) FROM transacoes WHERE obreiro_id = ? AND categoria = 'Mensalidade' AND strftime('%Y', data) = ?",
                (row['id'], str(ano_atual))
            ).iloc[0, 0]
            
            # Calcula meses devidos (do início do ano até o mês atual)
            meses_devidos = mes_atual
            
            # Calcula meses em atraso
            meses_atraso = max(0, meses_devidos - pagamentos_ano)
            
            if meses_atraso == 0:
                sit = "🟢 Em Dia"
                devido = 0.0
            elif meses_atraso <= 2:
                sit = f"🟡 Em Atraso ({meses_atraso} meses)"
                devido = meses_atraso * row['valor_mensalidade']
            else:
                sit = f"🔴 Inadimplente ({meses_atraso} meses)"
                devido = meses_atraso * row['valor_mensalidade']
                
        situacao_dados.append({
            "Irmão": row['nome'],
            "Grau": row['grau'],
            "Mensalidade Cadastrada": f"R$ {row['valor_mensalidade']:.2f}",
            "Status Financeiro": sit,
            "Saldo devedor": f"R$ {devido:.2f}"
        })
        
    df_situacao = pd.DataFrame(situacao_dados)
    st.table(df_situacao)
    
    st.markdown("---")
    st.subheader("🔧 Gerenciar Obreiros")
    
    # Selecionar obreiro para editar/excluir
    df_lista_obreiros = buscar_dados("SELECT id, nome, grau FROM obreiros")
    if not df_lista_obreiros.empty:
        obreiro_acao = st.selectbox("Selecione um obreiro para gerenciar:", 
                                    df_lista_obreiros['nome'].tolist())
        
        if obreiro_acao:
            obreiro_id_edit = df_lista_obreiros[df_lista_obreiros['nome'] == obreiro_acao]['id'].iloc[0]
            obreiro_dados = buscar_dados("SELECT * FROM obreiros WHERE id = ?", (obreiro_id_edit,))
            if obreiro_dados.empty:
                st.error("Obreiro não encontrado.")
            else:
                obreiro_dados = obreiro_dados.iloc[0]
                
                col_edit1, col_edit2 = st.columns(2)
                with col_edit1:
                    novo_nome = st.text_input("Nome", value=obreiro_dados['nome'])
                    novo_grau = st.selectbox("Grau", ["Aprendiz", "Companheiro", "Mestre", "Mestre Instalado"], 
                                           index=["Aprendiz", "Companheiro", "Mestre", "Mestre Instalado"].index(obreiro_dados['grau']))
                with col_edit2:
                    novo_valor = st.number_input("Valor Mensalidade", min_value=0.0, value=float(obreiro_dados['valor_mensalidade']))
                    novo_isento = st.checkbox("Isento/Remido", value=bool(obreiro_dados['status_isento']))
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("Atualizar Obreiro"):
                        status_isento_val = 1 if novo_isento else 0
                        if novo_isento: novo_valor = 0.0
                        
                        executar_comando("""
                            UPDATE obreiros SET nome = ?, grau = ?, valor_mensalidade = ?, status_isento = ? WHERE id = ?
                        """, (novo_nome, novo_grau, novo_valor, status_isento_val, obreiro_id_edit))
                        st.success("Obreiro atualizado com sucesso!")
                        st.rerun()
                
                with col_btn2:
                    if st.button("Excluir Obreiro", type="secondary"):
                        # Verificar se há transações vinculadas
                        transacoes_vinculadas = buscar_dados("SELECT COUNT(*) FROM transacoes WHERE obreiro_id = ?", 
                                                           (obreiro_id_edit,)).iloc[0, 0]
                        if transacoes_vinculadas > 0:
                            st.warning(f"Não é possível excluir: existem {transacoes_vinculadas} transações vinculadas a este obreiro.")
                        else:
                            executar_comando("DELETE FROM obreiros WHERE id = ?", (obreiro_id_edit,))
                            st.success("Obreiro excluído com sucesso!")
                            st.rerun()

# ==========================================
# MÓDULO 4: CADASTRAR IRMÃO
# ==========================================
elif escolha == "Cadastrar Irmão":
    st.subheader("📝 Adicionar Novo Irmão ao Quadro da Loja")
    
    col1, col2 = st.columns(2)
    with col1:
        nome_irmao = st.text_input("Nome Completo do Irmão")
        grau_irmao = st.selectbox("Grau", ["Aprendiz", "Companheiro", "Mestre", "Mestre Instalado"])
    with col2:
        val_mensalidade = st.number_input("Valor da Mensalidade Regular (R$)", min_value=0.0, value=100.0)
        isento = st.checkbox("Irmão Isento / Remido?")
        
    if st.button("Cadastrar Obreiro"):
        if nome_irmao:
            status_isento_val = 1 if isento else 0
            if isento: val_mensalidade = 0.0
            
            executar_comando("""
                INSERT INTO obreiros (nome, grau, valor_mensalidade, status_isento) 
                VALUES (?, ?, ?, ?)
            """, (nome_irmao, grau_irmao, val_mensalidade, status_isento_val))
            st.success(f"Irmão {nome_irmao} cadastrado com sucesso no Quadro!")
        else:
            st.error("Por favor, preencha o nome do irmão.")

# ==========================================
# MÓDULO 5: RELATÓRIOS FINANCEIROS
# ==========================================
elif escolha == "Relatórios Financeiros":
    st.subheader("📋 Relatórios para Prestação de Contas")
    
    # Seleção de tipo de relatório
    tipo_relatorio = st.selectbox("Tipo de Relatório", 
                                  ["Relatório Mensal", "Relatório Trimestral", "Relatório Anual", "Balancete Geral"])
    
    # Filtros de período
    col_filtro1, col_filtro2 = st.columns(2)
    with col_filtro1:
        data_inicio_rel = st.date_input("Data Início", value=date(2026, 1, 1))
    with col_filtro2:
        data_fim_rel = st.date_input("Data Fim", value=date.today())
    
    # Buscar dados filtrados
    df_relatorio = buscar_dados("SELECT * FROM transacoes WHERE data BETWEEN ? AND ? ORDER BY data",
                                (data_inicio_rel.strftime('%Y-%m-%d'), data_fim_rel.strftime('%Y-%m-%d')))
    df_relatorio['valor'] = df_relatorio['valor'].astype(float)
    df_relatorio['data'] = pd.to_datetime(df_relatorio['data'])
    
    if df_relatorio.empty:
        st.warning("Não há transações no período selecionado.")
    else:
        # Cálculos do relatório
        total_entradas_rel = df_relatorio[df_relatorio['tipo'] == 'Entrada']['valor'].sum()
        total_saidas_rel = df_relatorio[df_relatorio['tipo'] == 'Saída']['valor'].sum()
        saldo_rel = total_entradas_rel - total_saidas_rel
        
        # Resumo executivo
        st.markdown("### 📊 Resumo Executivo")
        col_r1, col_r2, col_r3 = st.columns(3)
        col_r1.metric("Total Receitas", formatar_moeda(total_entradas_rel))
        col_r2.metric("Total Despesas", formatar_moeda(total_saidas_rel))
        col_r3.metric("Saldo do Período", formatar_moeda(saldo_rel), 
                     delta=formatar_moeda(saldo_rel), delta_color="normal" if saldo_rel >= 0 else "inverse")
        
        st.markdown("---")
        
        # Detalhamento por categoria
        st.markdown("### 📈 Detalhamento por Categoria")
        
        col_cat1, col_cat2 = st.columns(2)
        
        with col_cat1:
            st.markdown("#### Receitas por Categoria")
            df_receitas = df_relatorio[df_relatorio['tipo'] == 'Entrada']
            if not df_receitas.empty:
                df_rec_cat = df_receitas.groupby('categoria').agg({
                    'valor': 'sum',
                    'id': 'count'
                }).rename(columns={'valor': 'Total', 'id': 'Qtd'})
                df_rec_cat = df_rec_cat.sort_values('Total', ascending=False)
                df_rec_cat['Total'] = df_rec_cat['Total'].apply(formatar_moeda)
                st.dataframe(df_rec_cat, use_container_width=True)
            else:
                st.info("Não há receitas no período")
        
        with col_cat2:
            st.markdown("#### Despesas por Categoria")
            df_despesas = df_relatorio[df_relatorio['tipo'] == 'Saída']
            if not df_despesas.empty:
                df_des_cat = df_despesas.groupby('categoria').agg({
                    'valor': 'sum',
                    'id': 'count'
                }).rename(columns={'valor': 'Total', 'id': 'Qtd'})
                df_des_cat = df_des_cat.sort_values('Total', ascending=False)
                df_des_cat['Total'] = df_des_cat['Total'].apply(formatar_moeda)
                st.dataframe(df_des_cat, use_container_width=True)
            else:
                st.info("Não há despesas no período")
        
        st.markdown("---")
        
        # Extrato completo
        st.markdown("### 📜 Extrato Completo do Período")
        df_extrato = df_relatorio.copy()
        df_extrato['data'] = df_extrato['data'].dt.strftime('%d/%m/%Y')
        
        # Ajustar nomes das colunas baseado no número real de colunas
        num_cols = len(df_extrato.columns)
        if num_cols == 8:
            df_extrato.columns = ["ID", "Data", "Tipo", "Categoria", "Descrição", "Valor", "ID Obreiro", "Data Cadastro"]
        else:
            df_extrato.columns = ["ID", "Data", "Tipo", "Categoria", "Descrição", "Valor", "ID Obreiro"]
        
        # Formatar valores
        df_extrato['Valor'] = df_extrato['Valor'].apply(lambda x: formatar_moeda(x))
        
        st.dataframe(df_extrato[["Data", "Tipo", "Categoria", "Descrição", "Valor"]], 
                    use_container_width=True, height=400)
        
        st.markdown("---")
        
        # Exportação
        st.markdown("### 📥 Exportar Relatório")
        col_exp1, col_exp2 = st.columns(2)
        
        with col_exp1:
            # Exportar para Excel
            df_export = df_relatorio.copy()
            df_export['data'] = df_export['data'].dt.strftime('%d/%m/%Y')
            
            # Ajustar nomes das colunas baseado no número real de colunas
            num_cols_export = len(df_export.columns)
            if num_cols_export == 8:
                df_export.columns = ["ID", "Data", "Tipo", "Categoria", "Descrição", "Valor", "ID Obreiro", "Data Cadastro"]
            else:
                df_export.columns = ["ID", "Data", "Tipo", "Categoria", "Descrição", "Valor", "ID Obreiro"]
            
            @st.cache_data
            def convert_df_to_csv(df):
                return df.to_csv(index=False).encode('utf-8')
            
            csv = convert_df_to_csv(df_export)
            
            st.download_button(
                label="📊 Baixar Relatório CSV",
                data=csv,
                file_name=f'relatorio_financeiro_{data_inicio_rel.strftime("%Y-%m-%d")}_a_{data_fim_rel.strftime("%Y-%m-%d")}.csv',
                mime='text/csv',
            )
        
        with col_exp2:
            st.info("📄 Funcionalidade de exportação PDF em desenvolvimento")
        
        # Informações adicionais para prestação de contas
        st.markdown("---")
        st.markdown("### ℹ️ Informações para Prestação de Contas")
        st.info(f"""
        **Período do Relatório:** {data_inicio_rel.strftime('%d/%m/%Y')} a {data_fim_rel.strftime('%d/%m/%Y')}
        
        **Total de Transações:** {len(df_relatorio)}
        
        **Maior Receita:** {formatar_moeda(df_relatorio[df_relatorio['tipo'] == 'Entrada']['valor'].max()) if not df_relatorio[df_relatorio['tipo'] == 'Entrada'].empty else 'N/A'}
        
        **Maior Despesa:** {formatar_moeda(df_relatorio[df_relatorio['tipo'] == 'Saída']['valor'].max()) if not df_relatorio[df_relatorio['tipo'] == 'Saída'].empty else 'N/A'}
        
        **Média de Entradas:** {formatar_moeda(df_relatorio[df_relatorio['tipo'] == 'Entrada']['valor'].mean()) if not df_relatorio[df_relatorio['tipo'] == 'Entrada'].empty else 'N/A'}
        
        **Média de Saídas:** {formatar_moeda(df_relatorio[df_relatorio['tipo'] == 'Saída']['valor'].mean()) if not df_relatorio[df_relatorio['tipo'] == 'Saída'].empty else 'N/A'}
        """)