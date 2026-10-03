from app.db import connect

TAG_MAX = 50


def normalize_tag(name):
    # «Горячий», «горячий » и «#Горячий» должны давать один и тот же тег.
    name = " ".join(name.split()).lstrip("#").strip().lower()
    return name[:TAG_MAX]


def add_tag(conn, lead_id, name):
    name = normalize_tag(name)
    if not name:
        return
    tag = conn.execute(
        "INSERT INTO tags (name) VALUES (%s) "
        "ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name RETURNING id",
        (name,),
    ).fetchone()
    conn.execute(
        "INSERT INTO lead_tags (lead_id, tag_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
        (lead_id, tag["id"]),
    )


def remove_tag(conn, lead_id, name):
    conn.execute(
        "DELETE FROM lead_tags WHERE lead_id = %s "
        "AND tag_id = (SELECT id FROM tags WHERE name = %s)",
        (lead_id, normalize_tag(name)),
    )


def list_used_tags():
    with connect() as conn:
        return conn.execute(
            "SELECT t.name, count(*) AS leads_count FROM tags t "
            "JOIN lead_tags lt ON lt.tag_id = t.id GROUP BY t.name ORDER BY t.name"
        ).fetchall()
