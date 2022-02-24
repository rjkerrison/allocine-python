import os
from flask import Flask

from app.main import get_showings

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello/<id>')
    def hello(id):
        return f'Hello, {id}!'

    @app.route('/showings/<id>')
    def showings(id):
        data = get_showings(id, format='json')
        response = app.response_class(
            response=data,
            status=200,
            mimetype='application/json'
        )
        return response

    return app



def main():
    create_app()

if __name__ == "__main__":
    main()
