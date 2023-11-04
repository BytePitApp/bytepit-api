FROM python:3.9

WORKDIR /devel

COPY ./requirements.txt /devel/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /devel/requirements.txt

COPY ./bytepit_api /devel/bytepit_api

CMD ["uvicorn", "bytepit_api.api:app", "--host", "0.0.0.0", "--port", "80"]