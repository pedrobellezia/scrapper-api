from starlette.requests import Request
import secrets
from starlette.responses import JSONResponse
from app.config.config import SECRET_KEY
from app.config.log import logger


async def auth(request: Request, call_next):
    logger.info(f"Received request: {request.method} {request.url}")
    if request.method != "GET":
        auth_token = request.headers.get("Authorization")

        if not auth_token or not auth_token.startswith("Bearer "):
            logger.warning("Authorization header ausente ou invalido")
            return JSONResponse(
                status_code=401,
                content={"detail": "Authorization header ausente ou invalido"},
            )

        token = auth_token.split(" ")[1]

        if not secrets.compare_digest(token, SECRET_KEY):
            logger.warning("Token de autenticacao invalido")
            return JSONResponse(
                status_code=401,
                content={"detail": "Token de autenticacao invalido"},
            )
    return await call_next(request)


__all__ = ["auth"]
