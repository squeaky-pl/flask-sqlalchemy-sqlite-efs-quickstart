FROM python:3.9.1-slim as dev

ADD requirements.txt .
RUN python -m pip install -r requirements.txt
WORKDIR /app
ENV PYTHONUNBUFFERED=1
