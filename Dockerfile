FROM python:3.10-slim

RUN mkdir /OpenTTD
WORKDIR /OpenTTD

COPY OpenTTD/requirements.txt .

RUN pip --no-cache-dir install -r requirements.txt

COPY OpenTTD/* .


CMD ["python", "./main.py"]