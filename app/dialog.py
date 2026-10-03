LIMITS = {"name": 200, "contact": 200, "request": 2000}
ASK = {
    "name": "Как вас зовут?",
    "contact": "Как с вами связаться? Телефон, e-mail или @username.",
    "request": "Опишите ваш запрос.",
}
NEXT = {"name": "contact", "contact": "request"}


def _command(text):
    if not text or not text.startswith("/"):
        return None
    return text.split()[0].split("@")[0].lower()


def handle(session, text):
    """Один шаг диалога.

    session: {"step", "name", "contact"} или None, если диалога нет.
    Возвращает (новая сессия или None, ответ, данные лида или None).
    """
    command = _command(text)
    if command == "/start":
        reply = "Здравствуйте! Оставьте заявку, это займёт минуту.\n" + ASK["name"]
        return {"step": "name", "name": None, "contact": None}, reply, None
    if command == "/cancel":
        return None, "Заявка отменена. Чтобы начать заново, отправьте /start.", None
    if command:
        return session, "Неизвестная команда. /start начинает заявку, /cancel отменяет её.", None
    if session is None:
        return None, "Чтобы оставить заявку, отправьте /start.", None

    step = session["step"]
    value = (text or "").strip()
    if not value:
        return session, "Ответьте, пожалуйста, текстом. " + ASK[step], None
    if len(value) > LIMITS[step]:
        return session, f"Слишком длинно, не больше {LIMITS[step]} символов. " + ASK[step], None

    if step == "request":
        lead = {"name": session["name"], "contact": session["contact"], "request": value}
        return None, "Спасибо! Заявка принята, мы свяжемся с вами.", lead
    new_session = {**session, step: value, "step": NEXT[step]}
    return new_session, ASK[new_session["step"]], None
