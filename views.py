from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from lnbits.core.models import User
from lnbits.decorators import check_user_exists
from pathlib import Path
import os

bakalari_rewards_generic_router = APIRouter()

# Absolutni cesta k templates/ teto extension
_EXT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
_EXT_TEMPLATES = str(_EXT_DIR / "templates")


def bakalari_rewards_renderer():
    from starlette.templating import Jinja2Templates
    from lnbits.settings import settings
    from lnbits.helpers import static_url_for, normalize_path
    from lnbits.utils.exchange_rates import currencies
    import json

    # Hledame lnbits/ slozku (rodic /app/lnbits/ nebo /app/)
    lnbits_path = Path(settings.lnbits_path)

    folders = [
        str(lnbits_path / "templates"),
        str(lnbits_path / "core" / "templates"),
        settings.extension_builder_working_dir_path.as_posix(),
        _EXT_TEMPLATES,
    ]
    # Odfiltrujeme neexistujici slozky
    folders = [f for f in folders if Path(f).exists()]

    t = Jinja2Templates(directory=folders)
    t.env.globals["static_url_for"] = static_url_for
    t.env.globals["normalize_path"] = normalize_path
    t.env.globals["SITE_TITLE"] = settings.lnbits_site_title
    t.env.globals["LNBITS_APPLE_TOUCH_ICON"] = settings.lnbits_apple_touch_icon
    t.env.globals["SETTINGS"] = settings.to_public().dict(by_alias=True)
    t.env.globals["CURRENCIES"] = list(currencies.keys())
    if settings.bundle_assets:
        t.env.globals["INCLUDED_JS"] = ["bundle.min.js"]
        t.env.globals["INCLUDED_CSS"] = ["bundle.min.css"]
        t.env.globals["INCLUDED_COMPONENTS"] = ["bundle-components.min.js"]
    else:
        vendor_filepath = lnbits_path / "static" / "vendor.json"
        with open(vendor_filepath) as vendor_file:
            vendor_files = json.loads(vendor_file.read())
        t.env.globals["INCLUDED_JS"] = vendor_files["js"]
        t.env.globals["INCLUDED_CSS"] = vendor_files["css"]
        t.env.globals["INCLUDED_COMPONENTS"] = vendor_files["components"]
    t.env.globals["LNBITS_DENOMINATION"] = settings.lnbits_denomination
    return t


@bakalari_rewards_generic_router.get("/", response_class=HTMLResponse)
async def index(request: Request, user: User = Depends(check_user_exists)):
    return bakalari_rewards_renderer().TemplateResponse(
        "bakalari_rewards/index.html",
        {"request": request, "user": user.dict()},
    )
