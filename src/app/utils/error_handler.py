from fastapi.responses import JSONResponse

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
