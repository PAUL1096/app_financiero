from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import db, Categoria

bp = Blueprint("categorias", __name__, url_prefix="/categorias")


@bp.route("/")
def listar():
    """Lista todas las categorías agrupadas por tipo"""
    categorias_ingreso = Categoria.query.filter_by(tipo="ingreso", padre_id=None).order_by(Categoria.nombre).all()
    categorias_gasto = Categoria.query.filter_by(tipo="gasto", padre_id=None).order_by(Categoria.nombre).all()

    return render_template(
        "categorias/listar.html",
        categorias_ingreso=categorias_ingreso,
        categorias_gasto=categorias_gasto
    )


@bp.route("/nueva", methods=["GET", "POST"])
def nueva():
    """Crear una nueva categoría"""
    if request.method == "POST":
        try:
            categoria = Categoria(
                nombre=request.form["nombre"].strip(),
                tipo=request.form["tipo"],
                color=request.form.get("color", "#6c757d"),
                icono=request.form.get("icono", "").strip() or None,
                padre_id=int(request.form["padre_id"]) if request.form.get("padre_id") else None
            )
            db.session.add(categoria)
            db.session.commit()
            flash("Categoría creada correctamente", "success")
            return redirect(url_for("categorias.listar"))

        except (ValueError, KeyError) as e:
            flash(f"Error al crear categoría: {str(e)}", "error")

    # Para seleccionar categoría padre
    categorias_padre = Categoria.query.filter_by(padre_id=None, activa=True).order_by(Categoria.tipo, Categoria.nombre).all()

    return render_template(
        "categorias/form.html",
        categoria=None,
        categorias_padre=categorias_padre
    )


@bp.route("/<int:id>/editar", methods=["GET", "POST"])
def editar(id):
    """Editar una categoría existente"""
    categoria = Categoria.query.get_or_404(id)

    if request.method == "POST":
        try:
            categoria.nombre = request.form["nombre"].strip()
            categoria.tipo = request.form["tipo"]
            categoria.color = request.form.get("color", "#6c757d")
            categoria.icono = request.form.get("icono", "").strip() or None
            categoria.padre_id = int(request.form["padre_id"]) if request.form.get("padre_id") else None
            categoria.activa = "activa" in request.form

            db.session.commit()
            flash("Categoría actualizada correctamente", "success")
            return redirect(url_for("categorias.listar"))

        except (ValueError, KeyError) as e:
            flash(f"Error al actualizar categoría: {str(e)}", "error")

    categorias_padre = Categoria.query.filter(
        Categoria.padre_id == None,
        Categoria.activa == True,
        Categoria.id != id
    ).order_by(Categoria.tipo, Categoria.nombre).all()

    return render_template(
        "categorias/form.html",
        categoria=categoria,
        categorias_padre=categorias_padre
    )


@bp.route("/<int:id>/toggle", methods=["POST"])
def toggle_activa(id):
    """Activar/desactivar una categoría"""
    categoria = Categoria.query.get_or_404(id)
    categoria.activa = not categoria.activa
    db.session.commit()
    estado = "activada" if categoria.activa else "desactivada"
    flash(f"Categoría {estado}", "success")
    return redirect(url_for("categorias.listar"))
