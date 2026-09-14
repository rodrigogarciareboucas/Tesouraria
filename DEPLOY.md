# Deploy em Nuvem - Sistema Financeiro

## 📋 Pré-requisitos

1. **Conta no Streamlit Cloud** (grátis em https://streamlit.io/cloud)
2. **Banco PostgreSQL na nuvem** (Supabase, Railway, ou Neon - todos têm planos gratuitos)

## 🔧 Configuração

### 1. Criar arquivo .env localmente

Crie um arquivo `.env` na raiz do projeto com as credenciais do PostgreSQL na nuvem:

```
POSTGRES_HOST=seu-host-postgres
POSTGRES_PORT=5432
POSTGRES_DATABASE=financas_loja
POSTGRES_USER=seu-usuario
POSTGRES_PASSWORD=sua-senha
```

### 2. Banco PostgreSQL na Nuvem

#### Opção A: Supabase (Recomendado - Grátis)
1. Acesse https://supabase.com
2. Crie um projeto novo
3. Vá em Settings > Database
4. Copie as credenciais (host, database, user, password)
5. Coloque no arquivo `.env`

#### Opção B: Railway (Grátis)
1. Acesse https://railway.app
2. Crie um novo projeto > Provision PostgreSQL
3. Copie as credenciais
4. Coloque no arquivo `.env`

#### Opção C: Neon (Grátis)
1. Acesse https://neon.tech
2. Crie um projeto
3. Copie a connection string
4. Coloque no arquivo `.env`

### 3. Deploy no Streamlit Cloud

1. **Faça upload do código no GitHub**
   - Crie um repositório no GitHub
   - Suba todos os arquivos do projeto
   - **NÃO suba o arquivo `.env`** (ele está no .gitignore)

2. **Configure o Streamlit Cloud**
   - Acesse https://share.streamlit.io
   - Clique em "New app"
   - Conecte seu repositório GitHub
   - Selecione o repositório do projeto
   - Main file path: `financeiro.py`

3. **Adicione as Secrets (Variáveis de Ambiente)**
   - No Streamlit Cloud, vá em Settings > Secrets
   - Adicione as seguintes secrets:
     ```
     POSTGRES_HOST=seu-host-postgres
     POSTGRES_PORT=5432
     POSTGRES_DATABASE=financas_loja
     POSTGRES_USER=seu-usuario
     POSTGRES_PASSWORD=sua-senha
     ```

4. **Deploy**
   - Clique em "Deploy"
   - Aguarde o build (primeiro demora ~2-3 minutos)
   - Acesse a URL gerada

## 🗄️ Migrar Dados para PostgreSQL na Nuvem

### Opção 1: Usar o módulo de Backup
1. No sistema local, acesse "💾 Backup e Restauração"
2. Baixe o backup PostgreSQL (.sql)
3. No banco na nuvem, execute o arquivo SQL

### Opção 2: Via psql (se tiver acesso)
```bash
psql -h seu-host -U seu-usuario -d financas_loja < backup.sql
```

## ✅ Verificação

Após o deploy:
1. Teste o login
2. Tente cadastrar um obreiro
3. Faça um lançamento no Livro Caixa
4. Verifique se os dados persistem

## 🔒 Segurança

- **Nunca** commitar o arquivo `.env`
- Usar senhas fortes no PostgreSQL
- O Streamlit Cloud protege as secrets automaticamente

## 📝 Troubleshooting

**Erro de conexão:**
- Verifique se as secrets estão configuradas corretamente
- Confirme se o PostgreSQL na nuvem aceita conexões externas
- Verifique se o firewall permite conexões

**Erro de build:**
- Verifique se `requirements.txt` está completo
- Confirme se todas as dependências estão listadas

## 🔄 Atualizações

Para atualizar o sistema:
1. Faça commit no GitHub
2. O Streamlit Cloud detecta automaticamente
3. Redeploy automático
