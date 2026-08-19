# -*- coding: utf-8 -*-
import mysql.connector

print("=== Tentando conectar à instância MySQL local via socket ===")
senhas_para_tentar = ['', 'root', '12345', 'password', 'mysql', 'admin', '123456', 'root123']

for senha in senhas_para_tentar:
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password=senha,
            unix_socket=r'C:\Users\Rodrigo  Garcia\Desktop\Maconaria\mysql_data\mysql.sock'
        )
        print(f"✓ Conectado à instância local! Senha: '{senha}'")
        
        cursor = conn.cursor()
        
        # Verificar bancos disponíveis
        cursor.execute("SHOW DATABASES")
        databases = [db[0] for db in cursor.fetchall()]
        print(f"  Bancos disponíveis: {databases}")
        
        # Verificar se o banco financas existe
        if 'financas' in databases:
            print("  ✓ Banco 'financas' encontrado")
            cursor.execute("USE financas")
            
            # Contar registros
            cursor.execute("SELECT COUNT(*) FROM obreiros")
            obreiros_count = cursor.fetchone()[0]
            print(f"  - Obreiros: {obreiros_count}")
            
            cursor.execute("SELECT COUNT(*) FROM transacoes")
            transacoes_count = cursor.fetchone()[0]
            print(f"  - Transações: {transacoes_count}")
            
            cursor.execute("SELECT COUNT(*) FROM categorias")
            categorias_count = cursor.fetchone()[0]
            print(f"  - Categorias: {categorias_count}")
        else:
            print("  ✗ Banco 'financas' não encontrado nesta instância")
        
        # Criar usuário rodrigo
        cursor.execute("DROP USER IF EXISTS 'rodrigo'@'localhost'")
        cursor.execute("CREATE USER 'rodrigo'@'localhost' IDENTIFIED BY '12345'")
        cursor.execute("GRANT ALL PRIVILEGES ON *.* TO 'rodrigo'@'localhost'")
        cursor.execute("FLUSH PRIVILEGES")
        print("✓ Usuário rodrigo criado com sucesso!")
        
        conn.commit()
        cursor.close()
        conn.close()
        exit(0)
        
    except Exception as e:
        print(f"  Senha '{senha}': {str(e)[:50]}...")
        continue

print("\n✗ Não foi possível conectar à instância local MySQL")
