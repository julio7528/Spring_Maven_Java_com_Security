import psycopg2
import sys

# --- Dados para o SESSION POOLER ---
DB_HOST = "aws-0-us-west-1.pooler.supabase.com"
DB_PORT = "5432" # Porta do Session Pooler
DB_NAME = "postgres"
DB_USER = "postgres.aulztkvhnsqkytzvkbhb" # Usuário do Pooler
DB_PASSWORD = "Marilda070765*#" # SUBSTITUA PELA SUA SENHA REAL DO POOLER!
# ---------------------------------

conn = None

try:
    print(f"Tentando conectar ao host '{DB_HOST}' (Session Pooler)...")
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    print("Conexão (Session Pooler) estabelecida com sucesso!")

    cur = conn.cursor()
    print("Executando 'SELECT version();'...")
    cur.execute("SELECT version();")
    db_version = cur.fetchone()
    print(f"Versão do PostgreSQL: {db_version[0]}")
    cur.close()

except psycopg2.OperationalError as e:
    print(f"--- ERRO AO CONECTAR (Session Pooler) ---", file=sys.stderr)
    print(f"Verifique os detalhes da conexão (host, porta 5432, db, user pooler, SENHA pooler) e a conectividade de rede.", file=sys.stderr)
    print(f"Detalhes do erro: {e}", file=sys.stderr)
# ... (resto dos blocos except/finally igual ao script anterior) ...
finally:
    if conn is not None:
        conn.close()
        print("Conexão fechada.")