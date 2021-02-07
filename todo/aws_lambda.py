from apig_wsgi import make_lambda_handler

from todo.api import app


def set_stage_prefix_middleware(app):
    def inner(environ, start_response):
        environ["SCRIPT_NAME"] = f"/{environ['apig_wsgi.request_context']['stage']}"

        return app(environ, start_response)

    return inner


app.wsgi_app = set_stage_prefix_middleware(app.wsgi_app)

handler = make_lambda_handler(app)
