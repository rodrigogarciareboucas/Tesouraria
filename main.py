# -*- coding: utf-8 -*-
from nicegui import ui, app
import sqlite3
import pandas as pd
from datetime import datetime, date
import plotly.express as px
import calendar

# ==========================================
# 1. CONFIGURAÇÕES E BANCO DE DADOS
# ==========================================
DB_PATH = 'financas_loja.db'

def init_db():
    """Inicializa o banco e garante que as colunas existam."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # 1. Cria tabelas caso não existam
        cursor.execute("CREATE TABLE IF NOT EXISTS transacoes (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT NOT NULL, tipo TEXT NOT NULL, categoria TEXT NOT NULL, descricao TEXT, valor REAL NOT NULL, mes_competencia TEXT, ano_competencia TEXT, id_sicredi TEXT UNIQUE)")
        cursor.execute("CREATE TABLE IF NOT EXISTS fila_sicredi (id INTEGER PRIMARY KEY AUTOINCREMENT, id_sicredi TEXT UNIQUE NOT NULL, data TEXT NOT NULL, tipo TEXT NOT NULL, descricao_banco TEXT NOT NULL, valor REAL NOT NULL, status_conciliacao TEXT DEFAULT 'Pendente')")
        cursor.execute("CREATE TABLE IF NOT EXISTS categorias (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT UNIQUE NOT NULL, tipo TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS obreiros (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, cim TEXT UNIQUE, grau TEXT, data_nascimento TEXT, telefone TEXT, email TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS mensalidades (id INTEGER PRIMARY KEY AUTOINCREMENT, cim_obreiro TEXT NOT NULL, mes_competencia TEXT NOT NULL, ano_competencia TEXT NOT NULL, valor REAL NOT NULL, status TEXT DEFAULT 'Pendente', data_pagamento TEXT, UNIQUE(cim_obreiro, mes_competencia, ano_competencia))")
        
        # 2. Adiciona colunas faltantes em 'obreiros' de forma segura
        try:
            cursor.execute("ALTER TABLE obreiros ADD COLUMN status TEXT")
        except sqlite3.OperationalError:
            pass # A coluna já existe, vida que segue
            
        conn.commit()

def buscar_dados(query, params=()):
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(query, conn, params=params)

def executar_comando(query, params=()):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return True

# ==========================================
# 2. UTILITÁRIOS E LAYOUT MESTRE
# ==========================================
def formatar_moeda(valor):
    """Formata valor em R$ sem usar lambdas in-line que quebram o Vue.js"""
    try:
        return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return "R$ 0,00"

def menu_lateral():
    """Cria o layout padrão (Header e Sidebar) que se repete em todas as páginas."""
    ui.dark_mode().enable()
    ui.colors(primary='#d4af37', secondary='#0f172a', accent='#1e293b', positive='#22c55e', negative='#ef4444')
    
    # Custom CSS 
    ui.add_head_html('''
        <style>
            ::-webkit-scrollbar { width: 8px; }
            ::-webkit-scrollbar-track { background: #0f172a; }
            ::-webkit-scrollbar-thumb { background: #d4af37; border-radius: 4px; }
            .q-table__container { background-color: #1e293b !important; color: white !important; }
            .q-table th { font-weight: bold !important; color: #d4af37 !important; }
        </style>
    ''')

    with ui.header(elevated=True).classes('bg-secondary text-primary items-center justify-between q-pa-sm'):
        with ui.row().classes('items-center'):
            ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').props('flat color=white')
            ui.label('Tesouraria - Jerônimo Rosado 1994').classes('text-xl font-bold font-serif ml-4')
        ui.icon('account_balance', size='sm').classes('text-primary mr-4')

    with ui.left_drawer(elevated=True).classes('bg-accent') as left_drawer:
        ui.label('Menu Principal').classes('text-primary text-lg font-bold q-pa-md mb-2')
        
        with ui.column().classes('w-full gap-2 px-2'):
            ui.button('Visão Geral', icon='dashboard', on_click=lambda: ui.navigate.to('/')).classes('w-full bg-secondary text-white')
            ui.button('Livro Caixa', icon='account_balance_wallet', on_click=lambda: ui.navigate.to('/caixa')).classes('w-full bg-secondary text-white')
            
            with ui.link(target='/conciliacao').props('target="_blank"').classes('w-full no-underline'):
                ui.button('Auditoria Sicredi ↗', icon='security').classes('w-full bg-blue-900 text-white font-bold')
            
            ui.separator().classes('my-2')
            ui.button('Categorias', icon='category', on_click=lambda: ui.navigate.to('/categorias')).classes('w-full bg-secondary text-white')
            ui.button('Carteira de Mensalidades', icon='payments', on_click=lambda: ui.navigate.to('/mensalidades')).classes('w-full bg-secondary text-white')
            ui.button('Cadastro de Obreiros', icon='people', on_click=lambda: ui.navigate.to('/obreiros')).classes('w-full bg-secondary text-white')
            ui.button('Aniversariantes', icon='cake', on_click=lambda: ui.navigate.to('/aniversariantes')).classes('w-full bg-secondary text-white')

# ==========================================
# 3. MÓDULO: DASHBOARD ( Rota: / )
# ==========================================
@ui.page('/')
def dashboard_page():
    menu_lateral()
    
    with ui.column().classes('w-full max-w-7xl mx-auto q-pa-lg'):
        ui.label('Visão Geral (Dashboard)').classes('text-3xl text-primary font-bold mb-6')
        
        df = buscar_dados("SELECT * FROM transacoes")
        if df.empty:
            ui.label('Nenhuma transação registrada no banco de dados.').classes('text-gray-400')
            return

        receitas = df[df['tipo'] == 'Entrada']['valor'].sum()
        despesas = df[df['tipo'] == 'Saída']['valor'].sum()
        saldo = receitas - despesas

        with ui.row().classes('w-full gap-6 mb-8'):
            with ui.card().classes('flex-1 bg-green-900 text-white p-6'):
                ui.label('Receitas Totais').classes('text-sm opacity-80 uppercase tracking-wider')
                ui.label(formatar_moeda(receitas)).classes('text-3xl font-bold mt-2')
            
            with ui.card().classes('flex-1 bg-red-900 text-white p-6'):
                ui.label('Despesas Totais').classes('text-sm opacity-80 uppercase tracking-wider')
                ui.label(formatar_moeda(despesas)).classes('text-3xl font-bold mt-2')
                
            with ui.card().classes('flex-1 bg-secondary text-primary border-2 border-primary p-6'):
                ui.label('Saldo Atualizado').classes('text-sm opacity-80 uppercase tracking-wider')
                ui.label(formatar_moeda(saldo)).classes('text-3xl font-bold mt-2')

        with ui.row().classes('w-full gap-6'):
            with ui.card().classes('flex-1 bg-accent p-4'):
                ui.label('Despesas por Categoria').classes('text-lg text-primary font-bold mb-4')
                df_saidas = df[df['tipo'] == 'Saída']
                if not df_saidas.empty:
                    df_agrupado = df_saidas.groupby('categoria')['valor'].sum().reset_index()
                    fig1 = px.pie(df_agrupado, values='valor', names='categoria', hole=0.4, 
                                  color_discrete_sequence=px.colors.sequential.YlOrRd)
                    fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
                    ui.plotly(fig1).classes('w-full h-80')
                else:
                    ui.label('Sem dados de saída.')

            with ui.card().classes('flex-1 bg-accent p-4'):
                ui.label('Fluxo de Caixa Diário').classes('text-lg text-primary font-bold mb-4')
                df_diario = df.groupby(['data', 'tipo'])['valor'].sum().reset_index()
                fig2 = px.bar(df_diario, x='data', y='valor', color='tipo', barmode='group',
                              color_discrete_map={'Entrada': '#22c55e', 'Saída': '#ef4444'})
                fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
                ui.plotly(fig2).classes('w-full h-80')

# ==========================================
# 4. MÓDULO: LIVRO CAIXA ( Rota: /caixa )
# ==========================================
@ui.page('/caixa')
def caixa_page():
    menu_lateral()
    
    @ui.refreshable
    def lista_transacoes():
        df = buscar_dados("SELECT id, data, tipo, categoria, descricao, valor FROM transacoes ORDER BY data DESC, id DESC LIMIT 100")
        if not df.empty:
            # Correção do Bug de Json Serialization (Aplicar na string ANTES da tabela)
            df['valor_formatado'] = df['valor'].apply(formatar_moeda)
            linhas = df.to_dict('records')
            
            colunas = [
                {'name': 'data', 'label': 'Data', 'field': 'data', 'align': 'left', 'sortable': True},
                {'name': 'tipo', 'label': 'Tipo', 'field': 'tipo', 'align': 'left'},
                {'name': 'categoria', 'label': 'Categoria', 'field': 'categoria', 'align': 'left'},
                {'name': 'descricao', 'label': 'Descrição', 'field': 'descricao', 'align': 'left'},
                {'name': 'valor', 'label': 'Valor (R$)', 'field': 'valor_formatado', 'align': 'right'},
            ]
            ui.table(columns=colunas, rows=linhas, row_key='id').classes('w-full bg-accent rounded-lg')
        else:
            ui.label('Livro caixa vazio.').classes('text-gray-400 italic')

    def salvar_transacao():
        if not all([inp_data.value, sel_tipo.value, sel_cat.value, inp_val.value]):
            ui.notify('Preencha todos os campos obrigatórios!', type='warning')
            return
        
        try:
            val_float = float(inp_val.value)
            dt_obj = datetime.strptime(inp_data.value, '%Y-%m-%d')
            executar_comando(
                "INSERT INTO transacoes (data, tipo, categoria, descricao, valor, mes_competencia, ano_competencia) VALUES (?,?,?,?,?,?,?)",
                (inp_data.value, sel_tipo.value, sel_cat.value, inp_desc.value, val_float, dt_obj.strftime('%B'), dt_obj.strftime('%Y'))
            )
            ui.notify('Lançamento salvo com sucesso!', type='positive')
            inp_desc.value = ''
            inp_val.value = 0
            lista_transacoes.refresh()
        except Exception as e:
            ui.notify(f'Erro ao salvar: {e}', type='negative')

    with ui.column().classes('w-full max-w-6xl mx-auto q-pa-lg'):
        ui.label('Livro Caixa').classes('text-3xl text-primary font-bold mb-4')
        
        with ui.expansion('Novo Lançamento Manual', icon='add_circle').classes('w-full bg-secondary text-white rounded-lg mb-6 shadow-md'):
            df_cats = buscar_dados("SELECT nome FROM categorias ORDER BY nome")
            cats = df_cats['nome'].tolist() if not df_cats.empty else ["Geral"]

            with ui.row().classes('w-full items-end gap-4 p-4'):
                inp_data = ui.input('Data', value=date.today().strftime('%Y-%m-%d')).props('type="date"').classes('flex-1')
                sel_tipo = ui.select(['Entrada', 'Saída'], label='Tipo', value='Entrada').classes('flex-1')
                sel_cat = ui.select(cats, label='Categoria', value=cats[0] if cats else None).classes('flex-1')
                inp_val = ui.number('Valor (R$)', format='%.2f').classes('flex-1')
            
            with ui.row().classes('w-full items-end gap-4 p-4 pt-0'):
                inp_desc = ui.input('Descrição do Lançamento').classes('flex-grow')
                ui.button('Salvar Lançamento', on_click=salvar_transacao).classes('bg-primary text-secondary font-bold px-8')

        ui.label('Últimas Transações').classes('text-xl text-primary font-bold mb-2')
        lista_transacoes()

# ==========================================
# 5. MÓDULO: CADASTRO DE OBREIROS ( Rota: /obreiros )
# ==========================================
@ui.page('/obreiros')
def obreiros_page():
    menu_lateral()
    
    @ui.refreshable
    def lista_obreiros():
        df = buscar_dados("SELECT id, cim, nome, grau, status FROM obreiros ORDER BY nome")
        if not df.empty:
            ui.table(
                columns=[
                    {'name': 'cim', 'label': 'CIM', 'field': 'cim', 'align': 'left'},
                    {'name': 'nome', 'label': 'Nome', 'field': 'nome', 'align': 'left'},
                    {'name': 'grau', 'label': 'Grau', 'field': 'grau', 'align': 'left'},
                    {'name': 'status', 'label': 'Status', 'field': 'status', 'align': 'left'},
                ],
                rows=df.to_dict('records'),
                row_key='id'
            ).classes('w-full bg-accent')
        else:
            ui.label('Nenhum obreiro cadastrado.').classes('text-gray-400')

    def salvar_obreiro():
        if not all([inp_nome.value, inp_cim.value]):
            ui.notify('Nome e CIM são obrigatórios.', type='warning')
            return
        try:
            executar_comando(
                "INSERT INTO obreiros (nome, cim, grau, status, data_nascimento) VALUES (?,?,?,?,?)",
                (inp_nome.value.upper(), inp_cim.value, sel_grau.value, sel_status.value, inp_nasc.value)
            )
            ui.notify('Obreiro cadastrado!', type='positive')
            inp_nome.value = ''
            inp_cim.value = ''
            lista_obreiros.refresh()
        except sqlite3.IntegrityError:
            ui.notify('Erro: CIM já existe no sistema.', type='negative')

    with ui.column().classes('w-full max-w-5xl mx-auto q-pa-lg'):
        ui.label('Cadastro de Obreiros').classes('text-3xl text-primary font-bold mb-4')
        
        with ui.card().classes('w-full bg-secondary mb-8 p-6'):
            ui.label('Adicionar Novo').classes('text-xl text-white mb-4')
            with ui.row().classes('w-full gap-4'):
                inp_nome = ui.input('Nome Completo').classes('flex-2 min-w-[300px]')
                inp_cim = ui.input('CIM').classes('flex-1')
                sel_grau = ui.select(['Aprendiz', 'Companheiro', 'Mestre', 'M.I.'], label='Grau', value='Aprendiz').classes('flex-1')
                sel_status = ui.select(['Ativo', 'Irregular', 'Licenciado', 'Adormecido'], label='Status', value='Ativo').classes('flex-1')
                inp_nasc = ui.input('Data Nascimento').props('type="date"').classes('flex-1')
            ui.button('Salvar Obreiro', on_click=salvar_obreiro).classes('bg-primary text-secondary font-bold mt-4')

        lista_obreiros()

# ==========================================
# 6. MÓDULO: MENSALIDADES (O MÓDULO RECUPERADO) ( Rota: /mensalidades )
# ==========================================
@ui.page('/mensalidades')
def mensalidades_page():
    menu_lateral()

    @ui.refreshable
    def lista_mensalidades():
        query = """
            SELECT m.id, o.nome, m.mes_competencia, m.ano_competencia, m.valor, m.status 
            FROM mensalidades m
            JOIN obreiros o ON m.cim_obreiro = o.cim
            ORDER BY m.ano_competencia DESC, m.mes_competencia DESC, o.nome
        """
        df = buscar_dados(query)
        if not df.empty:
            df['valor_fmt'] = df['valor'].apply(formatar_moeda)
            colunas = [
                {'name': 'nome', 'label': 'Obreiro', 'field': 'nome', 'align': 'left'},
                {'name': 'mes', 'label': 'Mês', 'field': 'mes_competencia', 'align': 'left'},
                {'name': 'ano', 'label': 'Ano', 'field': 'ano_competencia', 'align': 'left'},
                {'name': 'valor', 'label': 'Valor', 'field': 'valor_fmt', 'align': 'right'},
                {'name': 'status', 'label': 'Status', 'field': 'status', 'align': 'center'},
            ]
            ui.table(columns=colunas, rows=df.to_dict('records'), row_key='id').classes('w-full bg-accent rounded-lg mt-4')
        else:
            ui.label('Nenhuma mensalidade gerada ainda.').classes('text-gray-400 mt-4')

    with ui.column().classes('w-full max-w-6xl mx-auto q-pa-lg'):
        ui.label('Carteira de Mensalidades').classes('text-3xl text-primary font-bold mb-4')
        
        with ui.row().classes('w-full gap-4 items-end bg-secondary p-4 rounded-lg'):
            meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
            sel_mes = ui.select(meses, label='Mês', value=meses[datetime.now().month - 1]).classes('flex-1')
            inp_ano = ui.input('Ano', value=str(datetime.now().year)).classes('flex-1')
            inp_valor = ui.number('Valor Padrão (R$)', value=100.00, format='%.2f').classes('flex-1')
            
            def gerar_lote():
                if not all([sel_mes.value, inp_ano.value, inp_valor.value]):
                    ui.notify('Preencha os campos para gerar o lote.', type='warning')
                    return
                
                obreiros = buscar_dados("SELECT cim FROM obreiros WHERE status = 'Ativo'")
                if obreiros.empty:
                    ui.notify('Nenhum obreiro ativo para gerar mensalidade.', type='negative')
                    return
                
                inseridos = 0
                for _, row in obreiros.iterrows():
                    try:
                        executar_comando(
                            "INSERT INTO mensalidades (cim_obreiro, mes_competencia, ano_competencia, valor, status) VALUES (?,?,?,?,?)",
                            (row['cim'], sel_mes.value, inp_ano.value, float(inp_valor.value), 'Pendente')
                        )
                        inseridos += 1
                    except sqlite3.IntegrityError:
                        pass # Restrição UNIQUE barrou (já foi gerado para esse mês/ano/cim)
                
                ui.notify(f'{inseridos} mensalidades geradas com sucesso!', type='positive')
                lista_mensalidades.refresh()

            ui.button('Gerar Lote de Mensalidades', on_click=gerar_lote).classes('bg-primary text-secondary font-bold')

        lista_mensalidades()

# ==========================================
# 7. MÓDULO: ANIVERSARIANTES ( Rota: /aniversariantes )
# ==========================================
@ui.page('/aniversariantes')
def aniversariantes_page():
    menu_lateral()
    
    with ui.column().classes('w-full max-w-4xl mx-auto q-pa-lg'):
        mes_atual_num = datetime.now().month
        
        ui.label(f'Aniversariantes do Mês ({mes_atual_num:02d})').classes('text-3xl text-primary font-bold mb-6')
        
        df = buscar_dados("SELECT nome, data_nascimento, grau FROM obreiros WHERE data_nascimento IS NOT NULL AND data_nascimento != ''")
        
        if not df.empty:
            # Correção de Datas inválidas (Evita quebrar caso existam datas sujas no banco)
            df['dt_obj'] = pd.to_datetime(df['data_nascimento'], errors='coerce')
            df = df.dropna(subset=['dt_obj']) # Descarta lixos do banco temporariamente
            
            if not df.empty:
                df['mes_nasc'] = df['dt_obj'].dt.month
                df_mes = df[df['mes_nasc'] == mes_atual_num].sort_values(by='dt_obj')
                
                if not df_mes.empty:
                    for index, row in df_mes.iterrows():
                        dia = row['dt_obj'].day
                        with ui.card().classes('w-full bg-accent mb-2 flex flex-row items-center justify-between p-4'):
                            with ui.row().classes('items-center gap-4'):
                                ui.icon('cake', size='md').classes('text-primary')
                                with ui.column():
                                    ui.label(row['nome']).classes('text-lg font-bold text-white')
                                    ui.label(row['grau']).classes('text-sm text-gray-400')
                            ui.label(f"Dia {int(dia):02d}").classes('text-2xl text-primary font-bold')
                    return
                
        ui.label('Nenhum obreiro faz aniversário este mês.').classes('text-gray-400')


# ==========================================
# 8. MÓDULO: CONCILIAÇÃO SICREDI ( Rota: /conciliacao )
# ==========================================
@ui.page('/conciliacao')
def conciliacao_page():
    ui.dark_mode().enable()
    ui.colors(primary='#d4af37', secondary='#0f172a')
    
    with ui.header().classes('bg-blue-900 text-white items-center p-4'):
        ui.icon('account_balance', size='md').classes('mr-2 text-primary')
        ui.label('Auditoria e Conciliação - Integração Sicredi').classes('text-2xl font-bold')

    with ui.column().classes('w-full max-w-5xl mx-auto q-pa-lg mt-4'):
        df_pendentes = buscar_dados("SELECT * FROM fila_sicredi WHERE status_conciliacao = 'Pendente'")
        
        df_cats = buscar_dados("SELECT nome FROM categorias ORDER BY nome")
        lista_cats = df_cats['nome'].tolist() if not df_cats.empty else ["Geral", "Mensalidades", "Taxas", "Fornecedores"]

        if df_pendentes.empty:
            ui.label('✅ O caixa está 100% atualizado. Nenhuma transação bancária pendente.').classes('text-2xl text-green-500 font-bold mt-10')
            return

        for index, row in df_pendentes.iterrows():
            with ui.card().classes('w-full mb-4 bg-accent p-4'):
                with ui.row().classes('w-full items-center justify-between'):
                    with ui.column().classes('w-1/3'):
                        ui.label(f"{row['data']} - {row['tipo']}").classes('text-xs text-gray-400')
                        ui.label(row['descricao_banco']).classes('text-md font-bold text-white')
                    
                    with ui.column().classes('w-1/6'):
                        cor = 'text-green-400' if row['tipo'] == 'Entrada' else 'text-red-400'
                        ui.label(f"R$ {row['valor']:,.2f}").classes(f'text-xl font-bold {cor}')
                    
                    with ui.column().classes('w-1/3'):
                        select_cat = ui.select(lista_cats, label='Classificar em:').classes('w-full')
                    
                    with ui.column().classes('w-1/6 items-end'):
                        def confirmar(r=row, sel=select_cat):
                            if not sel.value:
                                ui.notify('Selecione uma categoria primeiro!', type='warning')
                                return
                            
                            executar_comando(
                                "INSERT INTO transacoes (data, tipo, categoria, descricao, valor, id_sicredi) VALUES (?,?,?,?,?,?)",
                                (r['data'], r['tipo'], sel.value, r['descricao_banco'], r['valor'], r['id_sicredi'])
                            )
                            executar_comando("UPDATE fila_sicredi SET status_conciliacao = 'Conciliado' WHERE id = ?", (r['id'],))
                            ui.notify('Conciliado com sucesso!', type='positive')
                            ui.navigate.to('/conciliacao') 

                        ui.button('Confirmar', on_click=confirmar).classes('bg-primary text-secondary font-bold')

# ==========================================
# 9. MÓDULO: CATEGORIAS ( Rota: /categorias )
# ==========================================
@ui.page('/categorias')
def categorias_page():
    menu_lateral()
    
    @ui.refreshable
    def lista_cats():
        df = buscar_dados("SELECT id, nome, tipo FROM categorias ORDER BY nome")
        if not df.empty:
            ui.table(columns=[
                {'name': 'nome', 'label': 'Nome da Categoria', 'field': 'nome', 'align': 'left'},
                {'name': 'tipo', 'label': 'Classificação', 'field': 'tipo', 'align': 'left'}
            ], rows=df.to_dict('records'), row_key='id').classes('w-full bg-accent max-w-2xl mt-6')

    def salvar_cat():
        if not inp_nome.value:
            ui.notify('Digite um nome para a categoria.', type='warning')
            return
        try:
            executar_comando("INSERT INTO categorias (nome, tipo) VALUES (?,?)", (inp_nome.value.strip(), sel_tipo.value))
            ui.notify('Categoria salva com sucesso.', type='positive')
            inp_nome.value = ''
            lista_cats.refresh()
        except sqlite3.IntegrityError:
            ui.notify('Categoria já existe!', type='negative')

    with ui.column().classes('w-full max-w-4xl mx-auto q-pa-lg'):
        ui.label('Gerenciar Categorias').classes('text-3xl text-primary font-bold mb-4')
        with ui.row().classes('w-full max-w-2xl gap-4 items-end bg-secondary p-4 rounded-lg'):
            inp_nome = ui.input('Nome da Nova Categoria').classes('flex-grow')
            sel_tipo = ui.select(['Entrada', 'Saída', 'Ambos'], value='Ambos', label='Tipo Base').classes('w-48')
            ui.button('Adicionar', on_click=salvar_cat).classes('bg-primary text-secondary font-bold mb-2')
        lista_cats()


# ==========================================
# INICIALIZAÇÃO DA APLICAÇÃO
# ==========================================
if __name__ in {"__main__", "__mp_main__"}:
    init_db()
    ui.run(title="Tesouraria MR", port=8080, reload=True, favicon='🏛️')