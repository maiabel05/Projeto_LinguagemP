import sqlite3

db_name = "midias.db"

def connect_db():
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    return conn

def inicializar_banco():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS midias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        formato TEXT NOT NULL,
        ano INTEGER,
        autor TEXT,
        status TEXT NOT NULL,
        progresso TEXT,
        nota REAL,
        resenha TEXT,
        atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    inicializar_banco()
    print("Banco de dados inicializado com sucesso.")