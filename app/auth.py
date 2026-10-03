import os
import secrets

from fastapi import HTTPException, Request


def check_password(candidate):
    return secrets.compare_digest(candidate.encode(), os.environ["CRM_PASSWORD"].encode())


def require_login(request: Request):
    if not request.session.get("auth"):
        raise HTTPException(303, headers={"Location": "/login"})
