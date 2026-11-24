from database import connect_db

def criar_midia(
        titulo: str,
        formato: str,
        ano: int | None,
        autor: str,
        status: str,
        progresso: str,
        nota: float | None,
        resenha: str,
):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO midias (titulo, formato, ano, autor, status, progresso, nota, resenha)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
    (titulo.strip(), formato, ano, autor.strip(), status, progresso.strip(), nota, resenha.strip()
     ),
    )

    conn.commit()
    conn.close()

def listar_status(status: str, termo: str = " ") -> list:
        conn = connect_db()
        cursor = conn.cursor()

        if termo.strip():
            cursor.execute("""
            SELECT * FROM midias
            WHERE status = ? AND titulo LIKE ?
            ORDER BY atualizado_em DESC, titulo ASC
            """, (status, f"%{termo.strip()}%"))
        else:
            cursor.execute("""
            SELECT * FROM midias
            WHERE status = ?
            ORDER BY atualizado_em DESC, titulo ASC
            """, (status,))

        resultados = cursor.fetchall()
        conn.close()
        return resultados

def buscar_por_id(midia_id: int):
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT * FROM midias
        WHERE id = ?
        """, (midia_id,))

        midia = cursor.fetchone()
        conn.close()
        return midia

def atualizar_midia(
        midia_id: int,
        titulo: str,
        formato: str,
        ano: int | None,
        autor: str,
        status: str,
        progresso: str,
        nota: float | None,
        resenha: str,
):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE midias
    SET titulo = ?, formato = ?, ano = ?, autor = ?, status = ?, progresso = ?, nota = ?, resenha = ?, atualizado_em = CURRENT_TIMESTAMP
    WHERE id = ?
    """,
    (titulo.strip(), formato, ano, autor.strip(), status, progresso.strip(), nota, resenha.strip(), midia_id)
    )

    conn.commit()
    conn.close()

def deletar_midia(midia_id: int):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM midias
    WHERE id = ?
    """, (midia_id,
    ))

    conn.commit()
    conn.close()