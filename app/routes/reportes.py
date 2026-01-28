from datetime import datetime
from flask import Blueprint, render_template, request, jsonify
from app.services.analisis import (
    obtener_resumen_dashboard,
    calcular_flujo_periodo,
    obtener_gastos_por_categoria,
    obtener_ingresos_por_categoria,
    obtener_tendencia_semanal,
    calcular_tasa_ahorro
)

bp = Blueprint("reportes", __name__, url_prefix="/reportes")


@bp.route("/dashboard")
def dashboard():
    """Vista principal del dashboard semanal"""
    resumen = obtener_resumen_dashboard()
    return render_template("reportes/dashboard.html", resumen=resumen)


@bp.route("/periodo")
def reporte_periodo():
    """Reporte personalizado por período"""
    fecha_desde = request.args.get("desde")
    fecha_hasta = request.args.get("hasta")

    if fecha_desde and fecha_hasta:
        desde = datetime.strptime(fecha_desde, "%Y-%m-%d").date()
        hasta = datetime.strptime(fecha_hasta, "%Y-%m-%d").date()

        datos = {
            "flujo": calcular_flujo_periodo(desde, hasta),
            "gastos_categoria": obtener_gastos_por_categoria(desde, hasta, limite=10),
            "ingresos_categoria": obtener_ingresos_por_categoria(desde, hasta),
            "tasa_ahorro": calcular_tasa_ahorro(desde, hasta)
        }
    else:
        datos = None

    return render_template(
        "reportes/periodo.html",
        datos=datos,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta
    )


@bp.route("/api/tendencia")
def api_tendencia():
    """API para obtener datos de tendencia (para gráficos)"""
    semanas = request.args.get("semanas", 8, type=int)
    tendencia = obtener_tendencia_semanal(semanas)
    return jsonify(tendencia)


@bp.route("/api/gastos-categoria")
def api_gastos_categoria():
    """API para obtener gastos por categoría (para gráficos)"""
    fecha_desde = request.args.get("desde")
    fecha_hasta = request.args.get("hasta")

    if fecha_desde and fecha_hasta:
        desde = datetime.strptime(fecha_desde, "%Y-%m-%d").date()
        hasta = datetime.strptime(fecha_hasta, "%Y-%m-%d").date()
    else:
        from app.services.analisis import obtener_rango_mes_actual
        desde, hasta = obtener_rango_mes_actual()

    gastos = obtener_gastos_por_categoria(desde, hasta, limite=10)
    return jsonify(gastos)
