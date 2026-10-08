import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()

login_manager.login_view = 'auth.login'
login_manager.login_message = 'Faça login para acessar esta página.'

def create_app(config_name='default'):
    app = Flask(__name__, template_folder='templates', static_folder='static')
    from app.config import config
    app.config.from_object(config[config_name])

    os.makedirs(app.config['DB_DIR'], exist_ok=True)
    os.makedirs(app.config['CSS_DIR'], exist_ok=True)
    os.makedirs(app.config['DOCS_DIR'], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    from app.views import main_bp, auth_bp, user_bp, pl_bp, admin_bp, api_bp, css_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(pl_bp, url_prefix='/pl')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(css_bp)

    from app.models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    @app.context_processor
    def inject_globals():
        from datetime import datetime
        def get_user_pref():
            try:
                from flask_login import current_user
                from app.models.css import UserCssPreference
                if current_user.is_authenticated:
                    pref = UserCssPreference.query.filter_by(user_id=current_user.id).first()
                    return pref
            except Exception:
                pass
            return None
        return {
            'app_name': app.config['APP_NAME'],
            'now': datetime.now(),
            'lgpd_link': app.config['LGPD_INTEGRAL_LINK'],
            'lgpd_summary': app.config['LGPD_SUMMARY'],
            'year': app.config['YEAR'],
            'get_user_pref': get_user_pref
        }

    with app.app_context():
        try:
            db.engine.execute('PRAGMA journal_mode=WAL;')
            db.engine.execute('PRAGMA foreign_keys=ON;')
        except Exception:
            pass

    return app
