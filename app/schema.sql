CREATE TABLE IF NOT EXISTS leads (
    id          SERIAL PRIMARY KEY,
    name        TEXT NOT NULL,
    contact     TEXT NOT NULL DEFAULT '',
    request     TEXT NOT NULL DEFAULT '',
    source      TEXT NOT NULL CHECK (source IN ('bot', 'manual')),
    tg_id       BIGINT,
    tg_username TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS tags (
    id   SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS lead_tags (
    lead_id INTEGER NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    tag_id  INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (lead_id, tag_id)
);

-- Шаг диалога бота хранится в БД: процесс на хостинге не держит состояние между запросами.
CREATE TABLE IF NOT EXISTS bot_sessions (
    tg_id      BIGINT PRIMARY KEY,
    step       TEXT NOT NULL,
    name       TEXT,
    contact    TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Telegram повторяет webhook при медленном ответе; update_id отсекает дубли.
CREATE TABLE IF NOT EXISTS processed_updates (
    update_id  BIGINT PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
