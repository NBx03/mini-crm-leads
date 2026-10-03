from datetime import timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app import leads

load_dotenv()

MSK = timezone(timedelta(hours=3))
NAME_MAX, CONTACT_MAX, REQUEST_MAX = 200, 200, 2000

app = FastAPI()
templates = Jinja2Templates(directory=Path(__file__).with_name("templates"))
templates.env.filters["msk"] = lambda dt: dt.astimezone(MSK).strftime("%d.%m.%Y %H:%M")


def render_index(request: Request, error=None, form=None, status_code=200):
    return templates.TemplateResponse(
        request,
        "leads.html",
        {"leads": leads.list_leads(), "error": error, "form": form or {}},
        status_code=status_code,
    )


@app.get("/")
def index(request: Request):
    return render_index(request)


@app.post("/leads")
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
