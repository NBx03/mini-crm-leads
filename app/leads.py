from app.db import connect


def list_leads():
    with connect() as conn:
        return conn.execute(
            "SELECT id, name, contact, request, source, tg_username, created_at "
            "FROM leads ORDER BY created_at DESC, id DESC"
        ).fetchall()


def create_lead(name, contact, request, source, tg_id=None, tg_username=None):
    with connect() as conn:
        row = conn.execute(
            "INSERT INTO leads (name, contact, request, source, tg_id, tg_username) "
            "VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
            (name, contact, request, source, tg_id, tg_username),
        ).fetchone()
        return row["id"]
