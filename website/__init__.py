from flask import Flask


def create_app():
    app = Flask(__name__)

    # # import the different routes
    # from .auth import auth
    # from .views import views

    # # register blueprints
    # app.register_blueprint(auth, url_prefix='/')
    # app.register_blueprint(views, url_prefix='/')

    return app
