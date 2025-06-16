# app/__init__.py

from flask import Flask
from flask_migrate import Migrate
from config import Config
from .models import db # Importa o db do mesmo pacote 'app'

# Inicializa a extensão de migração
migrate = Migrate()

def create_app():
    """
    Fábrica da aplicação: cria, configura e registra os componentes.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializa as extensões com a instância da aplicação
    db.init_app(app)
    migrate.init_app(app, db)

    # Importa e registra os Blueprints de cada área do site
    from .auth.routes import auth_bp
    from .cliente.routes import cliente_bp
    
    app.register_blueprint(auth_bp)
    
    # Todas as rotas do cliente serão acessadas com /cliente na frente
    # Ex: /cliente/dashboard, /cliente/deposito, etc.
    app.register_blueprint(cliente_bp, url_prefix='/cliente')

    return app
