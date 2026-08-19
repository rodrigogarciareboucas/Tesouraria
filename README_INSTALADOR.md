# Sistema Financeiro - Loja Jerônimo Rosado 1994
## Guia de Instalação e Build do Instalador

### Pré-requisitos

Para criar o instalador .exe, você precisa ter instalado:

1. **Python 3.9 ou superior** - [Download](https://www.python.org/downloads/)
2. **NSIS (Nullsoft Scriptable Install System)** - [Download](https://nsis.sourceforge.io/Download)
   - Instale em: `C:\Program Files (x86)\NSIS` ou `C:\Program Files\NSIS`

### Arquivos do Projeto

- `financeiro.py` - Aplicação principal (Streamlit)
- `init_db.py` - Script de inicialização do banco de dados
- `launcher.py` - Script que inicializa o banco e executa o sistema
- `requirements.txt` - Dependências do Python
- `build_exe.py` - Script PyInstaller para gerar executável
- `installer.nsi` - Script NSIS para criar instalador
- `build_installer.bat` - Script automatizado de build
- `logo.png` - Logo do sistema (opcional)

### Como Criar o Instalador

#### Método 1: Automatizado (Recomendado)

1. Abra o Prompt de Comando ou PowerShell na pasta do projeto
2. Execute o script de build:
   ```cmd
   build_installer.bat
   ```
3. Aguarde o processo completar
4. O instalador `.exe` será gerado na pasta atual

#### Método 2: Manual

**Passo 1: Instalar dependências**
```cmd
pip install -r requirements.txt
pip install pyinstaller pywin32
```

**Passo 2: Gerar executável**
```cmd
python build_exe.py
```

**Passo 3: Criar instalador com NSIS**
```cmd
"C:\Program Files (x86)\NSIS\makensis.exe" installer.nsi
```
ou
```cmd
"C:\Program Files\NSIS\makensis.exe" installer.nsi
```

### Como Usar o Instalador

1. Execute o arquivo `.exe` gerado
2. Siga o assistente de instalação
3. O sistema será instalado em `C:\Program Files\Sistema Financeiro - Loja Jerônimo Rosado 1994`
4. Atalhos serão criados:
   - Na Área de Trabalho
   - No Menu Iniciar

### Acesso Padrão

Após a instalação, acesse o sistema com:

- **E-mail**: `admin`
- **Senha**: `admin`

⚠️ **Importante**: Altere a senha do administrador após o primeiro acesso!

### Desinstalação

Para desinstalar o sistema:

1. Vá em **Painel de Controle** > **Programas e Recursos**
2. Selecione "Sistema Financeiro - Loja Jerônimo Rosado 1994"
3. Clique em **Desinstalar**

Ou use o atalho "Desinstalar" no Menu Iniciar.

### Estrutura do Banco de Dados

O banco de dados é criado automaticamente na primeira execução em:
```
C:\Program Files\Sistema Financeiro - Loja Jerônimo Rosado 1994\financas_loja.db
```

### Solução de Problemas

**Erro: NSIS não encontrado**
- Baixe e instale o NSIS em: https://nsis.sourceforge.io/Download
- Certifique-se de instalar em `C:\Program Files (x86)\NSIS`

**Erro: PyInstaller não encontrado**
- Execute: `pip install pyinstaller pywin32`

**Erro: Módulos Python não encontrados**
- Execute: `pip install -r requirements.txt`

**O sistema não inicia após instalação**
- Verifique se o Python está instalado no computador de destino
- O executável inclui o Python, mas algumas dependências podem precisar ser instaladas

### Suporte

Para dúvidas ou problemas, entre em contato com o desenvolvedor.

---

© 2026 Loja Jerônimo Rosado 1994
