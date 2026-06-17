from app.db.postgres import get_connection

def save_vector(text, embedding):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO documents
        (content, embedding)
        VALUES (%s,%s)
        """,
        (text, embedding.tolist())
    )

    conn.commit()

    cur.close()
    conn.close()