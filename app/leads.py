from app.db import connect


def list_leads(tag=None):
    # Фильтр через EXISTS, а не через JOIN: у лида должны остаться все его теги, а не только искомый.
    where = ""
    params = []
    if tag:
        where = (
            "WHERE EXISTS (SELECT 1 FROM lead_tags f JOIN tags ft ON ft.id = f.tag_id "
            "WHERE f.lead_id = l.id AND ft.name = %s)"
        )
        params.append(tag)
    with connect() as conn:
        return conn.execute(
            "SELECT l.id, l.name, l.contact, l.request, l.source, l.tg_username, l.created_at, "
            "COALESCE(array_agg(t.name ORDER BY t.name) FILTER (WHERE t.name IS NOT NULL), '{}') AS tags "
            "FROM leads l "
            "LEFT JOIN lead_tags lt ON lt.lead_id = l.id "
            "LEFT JOIN tags t ON t.id = lt.tag_id "
            f"{where} "
            "GROUP BY l.id ORDER BY l.created_at DESC, l.id DESC",
            params,
        ).fetchall()


def create_lead(name, contact, request, source, tg_id=None, tg_username=None):
    with connect() as conn:
        row = conn.execute(
            "INSERT INTO leads (name, contact, request, source, tg_id, tg_username) "
            "VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
            (name, contact, request, source, tg_id, tg_username),
        ).fetchone()
        return row["id"]
