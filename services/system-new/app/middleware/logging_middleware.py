

from fastapi import Request, Response
from fastapi.exceptions import HTTPException
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from strivelogger import StriveLogger


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        StriveLogger.info(f"{request.method} {request.url}")

        try:
            response = await call_next(request)
            return response
        except HTTPException as ex:
            if ex.status_code != status.HTTP_401_UNAUTHORIZED:
                StriveLogger.error("Exception encountered during request", ex)
            return Response(status_code=ex.status_code)
        except BaseException as ex:
            StriveLogger.error("Exception encountered during request", ex)

            return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
