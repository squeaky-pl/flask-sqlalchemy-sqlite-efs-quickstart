import uuid

import flask

from todo.db import Session
from todo.db import Todo

app = flask.Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    return "<h1>Test</p>"


def todo():
    session = Session()
    todo = Todo(name=f"My todo {uuid.uuid4()}")
    session.add(todo)
    session.commit()

    todos = session.query(Todo)

    return {"todos": [todo.to_json() for todo in todos]}
