import uuid

import flask

from todo.db import Session
from todo.db import Todo

app = flask.Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    session = Session()

    todos = session.query(Todo)

    return flask.render_template("index.html", todos=todos)


@app.route("/add", methods=["POST"])
def add():
    session = Session()

    todo = Todo(name=flask.request.form["name"])
    session.add(todo)
    session.commit()

    return flask.redirect(flask.url_for("index"))


@app.route("/todos.json", methods=["GET"])
def todo():
    session = Session()
    todo = Todo(name=f"My todo {uuid.uuid4()}")
    session.add(todo)
    session.commit()

    todos = session.query(Todo)

    return {"todos": [todo.to_json() for todo in todos]}
