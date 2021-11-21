from fastapi import HTTPException
from starlette import status


def abort_unauthorized():
    raise HTTPException(status_code=401, detail="Not authorized")


def abort_bad_request():
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad request")
