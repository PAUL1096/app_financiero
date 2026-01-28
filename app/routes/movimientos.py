from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import db, Movimiento, Cuenta, Categoria

bp = Blueprint("movimientos", __name__, url_prefix="/movimientos")


@bp.route("/")
def listar():
    """Lista todos los movimientos con filtros opcionales"""
    # Parámetros de filtro
    fecha_desde = request.args.get("desde")
    fecha_hasta = request.args.get("hasta")
    categoria_id = request.args.get("categoria")
    cuenta_id = request.args.get("cuenta")
    tipo = request.args.get("tipo")  # ingreso o gasto

    # Query base
    query = Movimiento.query

    # Aplicar filtros
    if fecha_desde:
        query = query.filter(Movimiento.fecha >= datetime.strptime(fecha_desde, "%Y-%m-%d").date())
    if fecha_hasta:
        query = query.filter(Movimiento.fecha <= datetime.strptime(fecha_hasta, "%Y-%m-%d").date())
    if categoria_id:
        query = query.filter(Movimiento.categoria_id == int(categoria_id))
    if cuenta_id:
        query = query.filter(Movimiento.cuenta_id == int(cuenta_id))
    if tipo:
        query = query.join(Categoria).filter(Categoria.tipo == tipo)

    # Ordenar por fecha descendente
    movimientos = query.order_by(Movimiento.fecha.desc(), Movimiento.id.desc()).all()

    # Datos para filtros
    categorias = Categoria.query.filter_by(activa=True).order_by(Categoria.tipo, Categoria.nombre).all()
    cuentas = Cuenta.query.filter_by(activa=True).all()

    return render_template(
        "movimientos/listar.html",
        movimientos=movimientos,
        categorias=categorias,
        cuentas=cuentas,
        filtros=request.args
    )


@bp.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    """Crear un nuevo movimiento"""
    if request.method == "POST":
        try:
            movimiento = Movimiento(
                fecha=datetime.strptime(request.form["fecha"], "%Y-%m-%d").date(),
                monto=float(request.form["monto"]),
                descripcion=request.form.get("descripcion", "").strip() or None,
                cuenta_id=int(request.form["cuenta_id"]),
                categoria_id=int(request.form["categoria_id"]),
                notas=request.form.get("notas", "").strip() or None
            )

            # Procesar etiquetas si existen
            etiquetas_raw = request.form.get("etiquetas", "").strip()
            if etiquetas_raw:
                movimiento.etiquetas = [e.strip() for e in etiquetas_raw.split(",") if e.strip()]

            db.session.add(movimiento)
            db.session.commit()
            flash("Movimiento registrado correctamente", "success")
            return redirect(url_for("movimientos.listar"))

        except (ValueError, KeyError) as e:
            flash(f"Error al registrar movimiento: {str(e)}", "error")

    # GET: mostrar formulario
    categorias = Categoria.query.filter_by(activa=True).order_by(Categoria.tipo, Categoria.nombre).all()
    cuentas = Cuenta.query.filter_by(activa=True).all()

    return render_template(
        "movimientos/form.html",
        movimiento=None,
        categorias=categorias,
        cuentas=cuentas,
        fecha_default=date.today().isoformat()
    )


@bp.route("/<int:id>/editar", methods=["GET", "POST"])
def editar(id):
    """Editar un movimiento existente"""
    movimiento = Movimiento.query.get_or_404(id)

    if request.method == "POST":
        try:
            movimiento.fecha = datetime.strptime(request.form["fecha"], "%Y-%m-%d").date()
            movimiento.monto = float(request.form["monto"])
            movimiento.descripcion = request.form.get("descripcion", "").strip() or None
            movimiento.cuenta_id = int(request.form["cuenta_id"])
            movimiento.categoria_id = int(request.form["categoria_id"])
            movimiento.notas = request.form.get("notas", "").strip() or None

            # Procesar etiquetas
            etiquetas_raw = request.form.get("etiquetas", "").strip()
            if etiquetas_raw:
                movimiento.etiquetas = [e.strip() for e in etiquetas_raw.split(",") if e.strip()]
            else:
                movimiento.etiquetas = None

            db.session.commit()
            flash("Movimiento actualizado correctamente", "success")
            return redirect(url_for("movimientos.listar"))

        except (ValueError, KeyError) as e:
            flash(f"Error al actualizar movimiento: {str(e)}", "error")

    categorias = Categoria.query.filter_by(activa=True).order_by(Categoria.tipo, Categoria.nombre).all()
    cuentas = Cuenta.query.filter_by(activa=True).all()

    return render_template(
        "movimientos/form.html",
        movimiento=movimiento,
        categorias=categorias,
        cuentas=cuentas,
        fecha_default=movimiento.fecha.isoformat()
    )


@bp.route("/<int:id>/eliminar", methods=["POST"])
def eliminar(id):
    """Eliminar un movimiento"""
    movimiento = Movimiento.query.get_or_404(id)
    db.session.delete(movimiento)
    db.session.commit()
    flash("Movimiento eliminado", "success")
    return redirect(url_for("movimientos.listar"))
