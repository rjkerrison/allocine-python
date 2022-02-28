import os
from flask import Flask, request
from app.cinemas import get_cinemas

from app.main import get_showings

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        CORS_HEADERS='Content-Type'
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

    # get cinema list
    @app.route('/cinemas/')
    def cinemas():
        data = get_cinemas(format='json')

        response = app.response_class(
            response=data,
            status=200,
            mimetype='application/json'
        )
        return response

    @app.route('/showings/<allocine_cinema_id>')
    def showings(allocine_cinema_id):
        args = request.args

        earliest_time = args.get("start", default=None, type=str)
        latest_time = args.get("end", default=None, type=str)

        data = get_showings(
            allocine_cinema_id,
            format='json',
            earliest_time=earliest_time,
            latest_time=latest_time,
        )
        response = app.response_class(
            response=data,
            status=200,
            mimetype='application/json',
        )
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    return app



def main():
    create_app()

if __name__ == "__main__":
    main()
