from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.crud import is_token_blacklisted

class TokenBlacklistMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = request.headers.get("Authorization")
        if token and token.startswith("Bearer "):
            token = token.split(" ")[1]
            if await is_token_blacklisted(token):
                return JSONResponse(
                    status_code=401, 
                    content={"detail": "Token has been blacklisted"}
                )
                # Raising the exception here caused Uvicorn to propagate it as an Internal Server Error
                # raise HTTPException(status_code=401, detail="Token has been blacklisted")

        return await call_next(request)
