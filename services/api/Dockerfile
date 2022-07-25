FROM python:3.11.0b4

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./yards_py /yards_py
RUN pip install yards_py/

COPY ./app /services/api/app

RUN python -m compileall /services/api/app

CMD uvicorn services.api.app.main:app --host 0.0.0.0 --port $PORT --workers 4