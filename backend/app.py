from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from models import db

jwt = JWTManager()


def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(Config)

    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    jwt.init_app(app)

    # Register blueprints (presentation layer -> routes)
    from routes.auth import auth_bp
    from routes.users import users_bp
    from routes.attractions import attractions_bp
    from routes.reviews import reviews_bp
    from routes.recommendation import recommendation_bp
    from routes.wishlist import wishlist_bp
    from routes.articles import articles_bp
    from routes.qa import qa_bp
    from routes.extra import tags_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(attractions_bp, url_prefix='/api/attractions')
    app.register_blueprint(reviews_bp, url_prefix='/api/reviews')
    app.register_blueprint(recommendation_bp, url_prefix='/api/recommendations')
    app.register_blueprint(wishlist_bp, url_prefix='/api/wishlist')
    app.register_blueprint(articles_bp, url_prefix='/api/articles')
    app.register_blueprint(qa_bp, url_prefix='/api/qa')
    app.register_blueprint(tags_bp, url_prefix='/api/tags')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    @app.route('/')
    def index():
        return send_from_directory('static', 'index.html')

    @app.route('/<path:path>')
    def serve_static(path):
        # If the requested path is a real static file (asset with an extension),
        # serve it. Otherwise fall back to index.html so the Vue Router can
        # handle the client-side route (SPA history-mode fallback).
        import os as _os
        candidate = _os.path.join(app.static_folder, path)
        if _os.path.isfile(candidate):
            return send_from_directory('static', path)
        return send_from_directory('static', 'index.html')

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=False, port=5000)
