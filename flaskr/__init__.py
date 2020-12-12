from flask import Flask
import os

def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'bookreviews.db')
    )

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    #register the database
    from . import db
    db.init_app(app)

    #register the auth Blueprint
    from . import auth
    app.register_blueprint(auth.bp)

    #register blog blueprint
    #from . import blog
    #app.register_blueprint(blog.bp)
    #app.add_url_rule('/', endpoint='index')

    return app
