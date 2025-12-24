from flask import Flask, request, session, redirect, url_for, flash
from flask_login import LoginManager, login_required, current_user
from flask_babel import Babel, get_locale
from modulos.extensions import db
from modulos.admin.models import Usuario

# Blueprints
from modulos.produtos import produtos_bp
from modulos.compras import compras_bp
from modulos.vendas import vendas_bp
from modulos.pagamentos import pagamentos_bp
from modulos.caixa import caixa_bp
from modulos.relatorios import relatorios_bp
from modulos.admin import admin_bp
from modulos.notificacoes import notificacoes_bp
from modulos.cotacoes import cotacoes_bp

from datetime import datetime

# =============================
# FACTORY PATTERN
# =============================
def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    # =====================================
    # BABEL (Internacionalização)
    # =====================================
    app.config["BABEL_DEFAULT_LOCALE"] = "pt"
    app.config["BABEL_DEFAULT_TIMEZONE"] = "Africa/Maputo"

    def select_locale():
        # Se o idioma vier via URL → sobrescreve
        if "lang" in request.args:
            session["lang"] = request.args.get("lang")

        # Se estiver salvo na sessão → usa
        if "lang" in session:
            return session["lang"]

        # Senão, tenta detectar automaticamente
        return request.accept_languages.best_match(["pt", "en", "fr"])

    babel = Babel(app, locale_selector=select_locale)

    # =====================================
    # Banco de dados
    # =====================================
    db.init_app(app)

    # =====================================
    # Login Manager
    # =====================================
    login_manager = LoginManager()
    login_manager.login_view = "admin.login_admin"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # =====================================
    # get_locale disponível nos templates
    # =====================================
    @app.context_processor
    def inject_get_locale():
        return dict(get_locale=get_locale)

    # =====================================
    # Função now() disponível nos templates
    # =====================================
    @app.context_processor
    def inject_now():
        return {'now': datetime.now}

    # =====================================
    # Registro dos Blueprints
    # =====================================
    app.register_blueprint(produtos_bp)
    app.register_blueprint(compras_bp)
    app.register_blueprint(vendas_bp)
    app.register_blueprint(pagamentos_bp)
    app.register_blueprint(caixa_bp)
    app.register_blueprint(relatorios_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(notificacoes_bp)
    app.register_blueprint(cotacoes_bp)
    # =====================================
    # Criação automática do banco + admin
    # =====================================
    with app.app_context():
        db.create_all()

        # Criar admin padrão se não existir
        if Usuario.query.first() is None:
            admin = Usuario(
                nome="Mutimbua",
                email="admin@lerp.com",
                is_admin=True
            )
            admin.set_senha("admin123")
            db.session.add(admin)
            db.session.commit()
            print("✔ Administrador padrão criado com sucesso!")

    # =====================================
    # Rota inicial
    # =====================================
    @app.route("/")
    @login_required
    def index():
        return redirect(url_for("admin.dashboard"))

    # =====================================
    # Rota para Trocar Idioma
    # =====================================
    @app.route("/change_language/<lang_code>")
    def change_language(lang_code):
        session["lang"] = lang_code
        # Volta para a mesma página, ou para login
        return redirect(request.referrer or url_for("admin.login_admin"))

    return app


# =============================
# Inicialização do servidor
# =============================
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)



