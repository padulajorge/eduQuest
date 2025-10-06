from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from dotenv import load_dotenv
from routers.chatApi import router as chat_router
from routers.documentsApi import router as documents_router
from routers.quizApi import router as quiz_router


load_dotenv()

app = FastAPI(title="EduQuest API", version="0.1.0")

# Rutas
app.include_router(quiz_router, prefix="/api")
app.include_router(chat_router, prefix="/chat")
app.include_router(documents_router, prefix="/api")


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )
