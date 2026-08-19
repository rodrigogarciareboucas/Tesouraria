# -*- coding: utf-8 -*-
import subprocess
import time
import mysql.connector
import os

print("=== Reset de Senha do Root MySQL ===\n")

# 1. Parar o serviço MySQL
print("1. Parando o serviço MySQL...")
try:
    subprocess.run(["net", "stop", "MySQL84"], check=True, capture_output=True)
    print("   ✓ Serviço MySQL84 parado")
except subprocess.CalledProcessError:
    try:
        subprocess.run(["net", "stop", "MySql"], check=True, capture_output=True)
        print("   ✓ Serviço MySql parado")
    except subprocess.CalledProcessError:
        print("   ✗ Não foi possível parar o serviço MySQL")
        exit(1)

# 2. Iniciar MySQL com --skip-grant-tables
print("\n2. Iniciando MySQL com --skip-grant-tables...")
mysql_path = r"C:\Program Files\MySQL\MySQL Server 8.4\bin\mysqld.exe"
datadir = r"C:\Users\Rodrigo  Garcia\Desktop\Maconaria\mysql_data"

# Tentar iniciar mysqld com skip-grant-tables
try:
    # Criar arquivo de configuração temporário
    temp_config = r"C:\Users\Rodrigo  Garcia\Desktop\Maconaria\mysql_data\my_temp.cnf"
    with open(temp_config, "w") as f:
        f.write("[mysqld]\n")
        f.write("skip-grant-tables\n")
        f.write("skip-networking\n")
    
    # Iniciar mysqld
    process = subprocess.Popen(
        [mysql_path, "--defaults-file=" + temp_config, "--datadir=" + datadir, "--console"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    
    print("   ✓ MySQL iniciado em modo de recuperação")
    time.sleep(5)  # Esperar o MySQL iniciar
    
except Exception as e:
    print(f"   ✗ Erro ao iniciar MySQL: {e}")
    # Tentar reiniciar o serviço normalmente
    subprocess.run(["net", "start", "MySQL84"], capture_output=True)
    exit(1)

# 3. Conectar e resetar senha
print("\n3. Resetando senha do root...")
try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        unix_socket=datadir + r'\mysql.sock'
    )
    cursor = conn.cursor()
    
    # Resetar senha do root
    cursor.execute("FLUSH PRIVILEGES")
    cursor.execute("ALTER USER 'root'@'localhost' IDENTIFIED BY 'root123'")
    
    # Criar usuário rodrigo
    cursor.execute("DROP USER IF EXISTS 'rodrigo'@'localhost'")
    cursor.execute("CREATE USER 'rodrigo'@'localhost' IDENTIFIED BY '12345'")
    cursor.execute("GRANT ALL PRIVILEGES ON *.* TO 'rodrigo'@'localhost'")
    cursor.execute("FLUSH PRIVILEGES")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("   ✓ Senha do root resetada para: root123")
    print("   ✓ Usuário rodrigo criado com senha: 12345")
    
except Exception as e:
    print(f"   ✗ Erro ao resetar senha: {e}")

# 4. Parar o MySQL em modo de recuperação
print("\n4. Parando MySQL em modo de recuperação...")
process.terminate()
time.sleep(3)

# Remover arquivo temporário
if os.path.exists(temp_config):
    os.remove(temp_config)

# 5. Reiniciar o serviço MySQL normalmente
print("\n5. Reiniciando o serviço MySQL...")
try:
    subprocess.run(["net", "start", "MySQL84"], check=True, capture_output=True)
    print("   ✓ Serviço MySQL reiniciado")
except subprocess.CalledProcessError:
    try:
        subprocess.run(["net", "start", "MySql"], check=True, capture_output=True)
        print("   ✓ Serviço MySql reiniciado")
    except subprocess.CalledProcessError as e:
        print(f"   ✗ Erro ao reiniciar: {e}")

print("\n=== Processo concluído ===")
print("Nova senha do root: root123")
print("Usuário rodrigo criado com senha: 12345")
