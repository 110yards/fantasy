FROM python:3.10

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./yards_py /yards_py
RUN pip install yards_py/

COPY ./app /services/system/app

RUN python -m compileall /services/system/app

CMD uvicorn services.system.app.main:app --host 0.0.0.0 --port $PORT --workers 20