import pprint
import uuid

from todo.db import Session
from todo.db import Todo


def todo():
    session = Session()
    todo = Todo(name=f"My todo {uuid.uuid4()}")
    session.add(todo)
    session.commit()

    todos = session.query(Todo)

    return {"todos": [todo.to_json() for todo in todos]}


if __name__ == "__main__":
    pprint.pprint(todo())
