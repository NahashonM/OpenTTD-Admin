FROM python:3.10-slim

RUN pip install discord
RUN pip install python-dotenv

COPY openttd /openttd

WORKDIR /openttd

CMD ['python', './main.py']