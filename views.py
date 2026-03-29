from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from lnbits.core.models import User
from lnbits.decorators import check_user_exists
from lnbits.helpers import template_renderer

bakalari_rewards_generic_router = APIRouter()

def bakalari_rewards_renderer():
    return template_renderer(["bakalari_rewards/templates"])

@bakalari_rewards_generic_router.get("/", response_class=HTMLResponse)
async def index(request: Request, user: User = Depends(check_user_exists)):
    return bakalari_rewards_renderer().TemplateResponse(
        "bakalari_rewards/index.html",
        {"request": request, "user": user.dict()},  # ← OPRAVENO: user.dict() místo user.json()
    )
