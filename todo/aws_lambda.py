from apig_wsgi import make_lambda_handler

from todo.api import app

handler = make_lambda_handler(app)
