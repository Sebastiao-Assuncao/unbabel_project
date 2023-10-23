from fastapi import FastAPI, HTTPException, Depends
from .auth.auth import auth_router
from .translation.translation import translation_router
from app.middleware import TokenBlacklistMiddleware

app = FastAPI()

app.add_middleware(TokenBlacklistMiddleware)

app.include_router(auth_router)
app.include_router(translation_router)