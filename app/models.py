from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Cuenta(db.Model):
    """Representa una cuenta financiera (efectivo, banco, tarjeta, etc.)"""
    __tablename__ = "cuentas"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # efectivo, banco, tarjeta, inversion
    saldo_inicial = db.Column(db.Float, default=0.0)
    activa = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    movimientos = db.relationship("Movimiento", backref="cuenta", lazy="dynamic")

    @property
    def saldo_actual(self):
        """Calcula el saldo actual basado en movimientos"""
        total = self.saldo_inicial
        for mov in self.movimientos:
            if mov.categoria and mov.categoria.tipo == "ingreso":
                total += mov.monto
            else:
                total -= mov.monto
        return total

    def __repr__(self):
        return f"<Cuenta {self.nombre}>"


class Categoria(db.Model):
    """Categoría de ingreso o gasto, con soporte para jerarquía"""
    __tablename__ = "categorias"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # ingreso, gasto
    color = db.Column(db.String(7), default="#6c757d")  # Color hex para gráficos
    icono = db.Column(db.String(50), nullable=True)  # Emoji o clase de icono
    padre_id = db.Column(db.Integer, db.ForeignKey("categorias.id"), nullable=True)
    activa = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación recursiva para subcategorías
    subcategorias = db.relationship(
        "Categoria",
        backref=db.backref("padre", remote_side=[id]),
        lazy="dynamic"
    )
    movimientos = db.relationship("Movimiento", backref="categoria", lazy="dynamic")

    def __repr__(self):
        return f"<Categoria {self.nombre} ({self.tipo})>"


class Movimiento(db.Model):
    """Representa un movimiento financiero (ingreso o gasto)"""
    __tablename__ = "movimientos"

    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False, default=date.today)
    monto = db.Column(db.Float, nullable=False)
    descripcion = db.Column(db.String(255), nullable=True)
    cuenta_id = db.Column(db.Integer, db.ForeignKey("cuentas.id"), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias.id"), nullable=False)
    etiquetas = db.Column(db.JSON, nullable=True)  # Lista flexible de etiquetas
    notas = db.Column(db.Text, nullable=True)  # Notas adicionales
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Movimiento {self.fecha} {self.monto}>"

    @property
    def es_ingreso(self):
        return self.categoria and self.categoria.tipo == "ingreso"


def init_db(app):
    """Inicializa la base de datos con datos por defecto"""
    with app.app_context():
        db.create_all()

        # Crear categorías por defecto si no existen
        if Categoria.query.count() == 0:
            categorias_default = [
                # Ingresos
                Categoria(nombre="Salario", tipo="ingreso", color="#28a745", icono="💰"),
                Categoria(nombre="Freelance", tipo="ingreso", color="#20c997", icono="💻"),
                Categoria(nombre="Inversiones", tipo="ingreso", color="#17a2b8", icono="📈"),
                Categoria(nombre="Otros ingresos", tipo="ingreso", color="#6f42c1", icono="💵"),
                # Gastos
                Categoria(nombre="Alimentación", tipo="gasto", color="#dc3545", icono="🍽️"),
                Categoria(nombre="Transporte", tipo="gasto", color="#fd7e14", icono="🚗"),
                Categoria(nombre="Vivienda", tipo="gasto", color="#e83e8c", icono="🏠"),
                Categoria(nombre="Servicios", tipo="gasto", color="#6c757d", icono="📱"),
                Categoria(nombre="Entretenimiento", tipo="gasto", color="#007bff", icono="🎬"),
                Categoria(nombre="Salud", tipo="gasto", color="#28a745", icono="🏥"),
                Categoria(nombre="Educación", tipo="gasto", color="#17a2b8", icono="📚"),
                Categoria(nombre="Otros gastos", tipo="gasto", color="#343a40", icono="📦"),
            ]
            for cat in categorias_default:
                db.session.add(cat)

        # Crear cuenta por defecto si no existe
        if Cuenta.query.count() == 0:
            cuenta_default = Cuenta(
                nombre="Efectivo",
                tipo="efectivo",
                saldo_inicial=0.0
            )
            db.session.add(cuenta_default)

        db.session.commit()
