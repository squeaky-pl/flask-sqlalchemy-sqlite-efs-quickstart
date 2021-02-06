from todo.__main__ import todo


def handler(event, context):
    return todo()
