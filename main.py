from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from dotenv import load_dotenv
from routers import chatApi

load_dotenv()

app = FastAPI()

app.include_router(chatApi.router, prefix="/chat")


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return JSONResponse(status_code=404, content={"detail": "Ruta no encontrada"})
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
