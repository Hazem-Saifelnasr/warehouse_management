from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="src/web/templates")


def handle_not_found_error(detail: str):
    return JSONResponse(
        status_code=404,
        content={"message": "Not Found", "detail": detail}
    )


def handle_forbidden_error(detail: str):
    return JSONResponse(
        status_code=403,
        content={"message": "Forbidden", "detail": detail}
    )


def error_page(request, status_code=None, message=None):
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "status_code": status_code,
            "message": message
        }
    )
