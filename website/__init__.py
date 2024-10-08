from flask import Flask

def create_app():
    app = Flask(__name__)

    # import the different routes
    from .auth import auth

    # register blueprints
    app.register_blueprint(auth, url_prefix='/')

    return app