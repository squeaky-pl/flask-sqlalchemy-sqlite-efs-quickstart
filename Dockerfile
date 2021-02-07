FROM python:3.9.1-slim as dev

ADD requirements.txt .
RUN python -m pip install -r requirements.txt
WORKDIR /app
ENV PYTHONUNBUFFERED=1

FROM dev as lambda

ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]
CMD [ "todo.aws_lambda.handler" ]

COPY todo /app/todo
