from fastapi import Request, Response
from fastapi.exceptions import HTTPException
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.core.logging import Logger


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        Logger.info(f"{request.method} {request.url}")

        try:
            response = await call_next(request)
            return response
        except HTTPException as ex:
            if ex.status_code != status.HTTP_401_UNAUTHORIZED:
                Logger.error("Exception encountered during request", ex)
            return Response(status_code=ex.status_code)
        except BaseException as ex:
            Logger.error("Exception encountered during request", ex)
            return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
