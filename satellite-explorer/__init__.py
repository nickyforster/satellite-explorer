import os
from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('config')
    app.config.from_pyfile('config.py')

    # @app.route('/hello')
    # def hello():
    #     return 'Hello, World'
    
    from . import search
    app.register_blueprint(search.bp)
    from . import results
    app.register_blueprint(results.bp)

    return app