import os
from datetime import timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode

from dotenv import load_dotenv
import psycopg
from fastapi import APIRouter, Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app import auth, leads, tags

load_dotenv()

MSK = timezone(timedelta(hours=3))
NAME_MAX, CONTACT_MAX, REQUEST_MAX = 200, 200, 2000

app = FastAPI()
# Сессия лежит в подписанной cookie: на Vercel нет общей памяти между запросами.
app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ["SESSION_SECRET"],
    https_only=bool(os.environ.get("VERCEL")),
)
crm = APIRouter(dependencies=[Depends(auth.require_login)])
templates = Jinja2Templates(directory=Path(__file__).with_name("templates"))
templates.env.filters["msk"] = lambda dt: dt.astimezone(MSK).strftime("%d.%m.%Y %H:%M")


def index_url(tag_filter):
    return "/?" + urlencode({"tag": tag_filter}) if tag_filter else "/"


def render_index(request: Request, tag_filter="", error=None, form=None, status_code=200):
    return templates.TemplateResponse(
        request,
        "leads.html",
        {
            "leads": leads.list_leads(tag_filter or None),
            "used_tags": tags.list_used_tags(),
            "tag_filter": tag_filter,
            "error": error,
            "form": form or {},
        },
        status_code=status_code,
    )


@app.get("/login")
def login_form(request: Request):
    return templates.TemplateResponse(request, "login.html", {})


@app.post("/login")
def login(request: Request, password: str = Form("")):
    if not auth.check_password(password):
        return templates.TemplateResponse(
            request, "login.html", {"error": "Неверный пароль"}, status_code=401
        )
    request.session["auth"] = True
    return RedirectResponse("/", status_code=303)


@crm.get("/")
def index(request: Request, tag: str = ""):
    return render_index(request, tags.normalize_tag(tag))


@crm.post("/leads")
def add_lead(
    request: Request,
    name: str = Form(""),
    contact: str = Form(""),
    lead_request: str = Form("", alias="request"),
):
    name, contact, lead_request = name.strip(), contact.strip(), lead_request.strip()
    if not name:
        form = {"name": name, "contact": contact, "request": lead_request}
        return render_index(request, error="Укажите имя", form=form, status_code=422)
    leads.create_lead(
        name[:NAME_MAX], contact[:CONTACT_MAX], lead_request[:REQUEST_MAX], "manual"
    )
    return RedirectResponse("/", status_code=303)


@crm.post("/leads/{lead_id}/tags")
def add_lead_tag(lead_id: int, tag: str = Form(""), tag_filter: str = Form("")):
    try:
        tags.add_tag(lead_id, tag)
    except psycopg.errors.ForeignKeyViolation:
        raise HTTPException(404, "Лид не найден")
    return RedirectResponse(index_url(tag_filter), status_code=303)


@crm.post("/leads/{lead_id}/tags/remove")
def remove_lead_tag(lead_id: int, tag: str = Form(""), tag_filter: str = Form("")):
    tags.remove_tag(lead_id, tag)
    return RedirectResponse(index_url(tag_filter), status_code=303)


app.include_router(crm)
