from app.dialog import ASK, LIMITS, handle


def run(*messages, session=None):
    """Прогоняет сообщения через диалог, возвращает (сессия, последний ответ, лид)."""
    reply = lead = None
    for text in messages:
        session, reply, lead = handle(session, text)
    return session, reply, lead


def test_full_dialog_creates_lead():
    session, reply, lead = run("/start", "Анна", "+7 900 000-00-00", "Нужна реклама")
    assert session is None
    assert lead == {"name": "Анна", "contact": "+7 900 000-00-00", "request": "Нужна реклама"}
    assert "принята" in reply


def test_start_asks_name():
    session, reply, lead = run("/start")
    assert session["step"] == "name"
    assert ASK["name"] in reply
    assert lead is None


def test_steps_follow_in_order():
    session, reply, _ = run("/start", "Анна")
    assert session["step"] == "contact" and reply == ASK["contact"]
    session, reply, _ = run("@anna", session=session)
    assert session["step"] == "request" and reply == ASK["request"]


def test_values_are_stripped():
    _, _, lead = run("/start", "  Анна ", " @anna ", "  запрос  ")
    assert lead == {"name": "Анна", "contact": "@anna", "request": "запрос"}


def test_start_in_the_middle_resets_dialog():
    session, _, _ = run("/start", "Анна", "@anna")
    session, reply, _ = run("/start", session=session)
    assert session == {"step": "name", "name": None, "contact": None}
    assert ASK["name"] in reply


def test_cancel_drops_session():
    session, reply, lead = run("/start", "Анна", "/cancel")
    assert session is None and lead is None
    assert "отменена" in reply


def test_text_without_session_asks_for_start():
    session, reply, lead = run("привет")
    assert session is None and lead is None
    assert "/start" in reply


def test_non_text_repeats_question():
    session, reply, lead = run("/start", None)
    assert session["step"] == "name" and lead is None
    assert reply.endswith(ASK["name"])


def test_empty_text_repeats_question():
    session, reply, _ = run("/start", "Анна", "   ")
    assert session["step"] == "contact"
    assert reply.endswith(ASK["contact"])


def test_too_long_value_is_rejected_not_truncated():
    session, reply, lead = run("/start", "я" * (LIMITS["name"] + 1))
    assert session["step"] == "name" and session["name"] is None and lead is None
    assert str(LIMITS["name"]) in reply


def test_value_at_limit_is_accepted():
    session, _, _ = run("/start", "я" * LIMITS["name"])
    assert session["step"] == "contact"


def test_unknown_command_keeps_session():
    session, reply, _ = run("/start", "Анна", "/help")
    assert session == {"step": "contact", "name": "Анна", "contact": None}
    assert "/cancel" in reply


def test_command_with_bot_name_and_payload():
    session, _, _ = run("/start@mini_crm_coolbot")
    assert session["step"] == "name"
    session, _, _ = run("/START promo")
    assert session["step"] == "name"


def test_command_is_not_taken_as_answer():
    session, _, _ = run("/start", "/cancel@mini_crm_coolbot")
    assert session is None
