# Instruções para Automação no Windows (Task Scheduler)

Como você está usando Windows, usaremos o **Task Scheduler** (Agendador de Tarefas) em vez do cron do Linux.

## Passo 1: Abrir o Task Scheduler

1. Pressione `Win + R` e digite `taskschd.msc`
2. Pressione Enter para abrir o Agendador de Tarefas do Windows

## Passo 2: Criar Nova Tarefa

1. No painel direito, clique em **"Criar Tarefa Básica"**
2. Nome: `Sincronizacao Sicredi`
3. Descrição: `Sincroniza extrato bancário do Sicredi a cada 30 minutos`
4. Clique em **Avançar**

## Passo 3: Configurar Gatilho (Quando executar)

1. Selecione **"Diariamente"**
2. Clique em **Avançar**
3. Configure para iniciar às 08:00
4. Repetir a cada: **30 minutos**
5. Por um período de: **Indeterminado**
6. Clique em **Avançar**

## Passo 4: Configurar Ação (O que executar)

1. Selecione **"Iniciar um programa"**
2. Clique em **Avançar**
3. **Programa/script:** `python.exe`
   - Caminho completo (exemplo): `C:\Python311\python.exe` ou `C:\Users\Rodrigo  Garcia\AppData\Local\Programs\Python\Python311\python.exe`
   - Para encontrar seu caminho: abra CMD e digite `where python`
4. **Adicionar argumentos:**
   ```
   "C:\Users\Rodrigo  Garcia\Desktop\Maconaria\sync_sicredi.py"
   ```
5. **Iniciar em (opcional):**
   ```
   C:\Users\Rodrigo  Garcia\Desktop\Maconaria
   ```
6. Clique em **Avançar**

## Passo 5: Finalizar

1. Revise as configurações
2. Marque **"Abrir a caixa de diálogo Propriedades desta tarefa quando eu clicar em Concluir"**
3. Clique em **Concluir**

## Passo 6: Configurações Avançadas (Importante)

Na janela de Propriedades que abriu:

1. Aba **Geral:**
   - Marque **"Executar independentemente do login do usuário"**
   - Marque **"Executar com os privilégios mais altos"**

2. Aba **Condições:**
   - Desmarque **"Iniciar o computador apenas se estiver conectado à rede de energia"** (se for desktop)
   - Desmarque **"Iniciar a tarefa apenas se o computador estiver conectado à rede"** (se tiver internet sempre)

3. Aba **Configurações:**
   - Marque **"Permitir que a tarefa seja executada sob demanda"**
   - Marque **"Executar a tarefa assim que possível após uma inicialização agendada"**
   - Se a tarefa falhar, reiniciar a tarefa a cada: **5 minutos**
   - Tentar reiniciar até: **3 vezes**

4. Clique em **OK** e digite sua senha de Windows se solicitado

## Passo 7: Testar Manualmente

1. No Task Scheduler, encontre sua tarefa `Sincronizacao Sicredi`
2. Clique com botão direito → **"Executar"**
3. Verifique se o arquivo de log foi criado em `C:\Users\Rodrigo  Garcia\Desktop\Maconaria\logs\sync_sicredi.log`
4. Abra o log para verificar se funcionou

## Passo 8: Verificar Dependências

Antes de executar, certifique-se de que:

1. **Python está instalado** e no PATH
2. **Bibliotecas instaladas:**
   ```cmd
   pip install requests python-dotenv
   ```
3. **Arquivo .env** está configurado com suas credenciais reais do Sicredi
4. **Certificado digital** está no caminho especificado no .env

## Solução de Problemas

### Tarefa não executa:
- Verifique o caminho do python.exe com `where python`
- Verifique se as bibliotecas estão instaladas
- Verifique o log em `logs/sync_sicredi.log`

### Erro de certificado:
- Verifique se o caminho do certificado no .env está correto
- Verifique se o arquivo .pem existe e é acessível

### Erro de autenticação:
- Verifique se CLIENT_ID e CLIENT_SECRET estão corretos no .env
- Verifique se o certificado é válido e não expirou
