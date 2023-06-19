from services.api.app.domain.repositories.user_repository import create_user_repository
from typing import List, Union
from services.api.app.core.role import Role
from yards_py.core.abort import abort_unauthorized
from fastapi import Request
from firebase_admin import auth
from yards_py.core.logging import Logger
from functools import wraps
from starlette_context import context

anonymous_endpoints = [
    "",
    "/login",
    "/user/register/email",
    "/user/exists",
    "/news",
]

anonymous_prefixes = [
    "/projection",
    "/score",
]


def check_token(req: Request):
    if req.method == "OPTIONS":  # don't check auth for CORS requests
        return

    if __get_token(req):
        return

    if anonymous_allowed(req):
        return

    abort_unauthorized()


def anonymous_allowed(req: Request):
    path = req.scope.get("path", "")

    if path.endswith("/"):
        path = path[:-1]

    if path in anonymous_endpoints:
        return True

    for prefix in anonymous_prefixes:
        if path.startswith(prefix):
            return True

    return False


def __get_token(request: Request):
    if "Authorization" not in request.headers:
        return None

    header = request.headers["Authorization"]

    try:
        parts = header.split(" ")
        if len(parts) < 2:
            Logger.warn("Invalid bearer token (less than 2 parts)")
            return None

        token = parts[1]
        # Logger.info(token)
        token = auth.verify_id_token(token, check_revoked=True)
        uid = token["uid"]
        request.state.uid = uid
        context.data["user_id"] = uid
        return token

    except auth.ExpiredIdTokenError:
        Logger.warn("Expired token encountered")
    except auth.InvalidIdTokenError:
        Logger.warn("Invalid token encountered")
    except BaseException as ex:
        Logger.error("Exception occurred while decoding token", exc_info=ex)
        return None


def get_current_user_id(request: Request) -> str:
    return request.state.uid


def require_role(roles: Union[str, List[Role]], **kwargs):
    '''
    request: Request must be in the route params
    '''
    def decorator(function):
        @wraps(function)
        async def wrapper(**kwargs):
            request = kwargs.get("request", None)

            if not request:
                abort_unauthorized()

            current_user_id = get_current_user_id(request)
            if not current_user_id:
                abort_unauthorized()

            user_repo = create_user_repository()

            roles_to_check = roles
            if not isinstance(roles, List):
                roles_to_check = [roles]

            allowed = False
            user = user_repo.get(current_user_id)

            if not user:
                return abort_unauthorized()

            for role in roles_to_check:
                # this could be better
                if role == Role.admin and user.is_admin:
                    allowed = True
                    break

            if not allowed:
                abort_unauthorized()

            return await function(**kwargs)
        return wrapper
    return decorator
