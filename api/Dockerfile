FROM gcr.io/mdryden-ci/fastapi-base:latest

COPY requirements.txt /requirements.txt
RUN pip install -r requirements.txt

COPY ./app /fantasy_api_mono/app

RUN python -m compileall /fantasy_api_mono/app

ENV APP="fantasy_api_mono.app.main:app"