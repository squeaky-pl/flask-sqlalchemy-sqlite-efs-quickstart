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


@app.route("/delete/<int:todo_id>", methods=["GET"])
def delete(todo_id):
    session = Session()

    todo = session.query(Todo).get(todo_id)
    session.delete(todo)
    session.commit()

    return flask.redirect(flask.url_for("index"))


@app.route("/todos.json", methods=["GET"])
def todo():
    session = Session()

    todos = session.query(Todo)

    return {"todos": [todo.to_json() for todo in todos]}
