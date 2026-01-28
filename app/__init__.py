from flask import Flask
from config import Config
from app.models import db, init_db


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializar extensiones
    db.init_app(app)

    # Registrar blueprints
    from app.routes import movimientos, categorias, reportes
    app.register_blueprint(movimientos.bp)
    app.register_blueprint(categorias.bp)
    app.register_blueprint(reportes.bp)

    # Ruta principal redirige al dashboard
    @app.route("/")
    def index():
        from flask import redirect, url_for
        return redirect(url_for("reportes.dashboard"))

    # Inicializar base de datos
    init_db(app)

    # Filtros personalizados para templates
    @app.template_filter("moneda")
    def formato_moneda(valor):
        """Formatea un número como moneda"""
        if valor is None:
            return "$0.00"
        return f"${valor:,.2f}"

    @app.template_filter("fecha_corta")
    def formato_fecha_corta(fecha):
        """Formatea fecha como dd/mm/yyyy"""
        if fecha is None:
            return ""
        return fecha.strftime("%d/%m/%Y")

    return app
