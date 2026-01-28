from datetime import date, timedelta
from sqlalchemy import func
from app.models import db, Movimiento, Categoria, Cuenta


def obtener_rango_semana_actual():
    """Retorna el inicio y fin de la semana actual (lunes a domingo)"""
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    return inicio_semana, fin_semana


def obtener_rango_mes_actual():
    """Retorna el inicio y fin del mes actual"""
    hoy = date.today()
    inicio_mes = hoy.replace(day=1)
    # Último día del mes
    if hoy.month == 12:
        fin_mes = hoy.replace(day=31)
    else:
        fin_mes = hoy.replace(month=hoy.month + 1, day=1) - timedelta(days=1)
    return inicio_mes, fin_mes


def calcular_balance_total():
    """Calcula el balance total de todas las cuentas activas"""
    cuentas = Cuenta.query.filter_by(activa=True).all()
    return sum(cuenta.saldo_actual for cuenta in cuentas)


def calcular_flujo_periodo(fecha_inicio, fecha_fin):
    """Calcula ingresos y gastos en un período"""
    movimientos = Movimiento.query.filter(
        Movimiento.fecha >= fecha_inicio,
        Movimiento.fecha <= fecha_fin
    ).all()

    ingresos = sum(m.monto for m in movimientos if m.es_ingreso)
    gastos = sum(m.monto for m in movimientos if not m.es_ingreso)

    return {
        "ingresos": ingresos,
        "gastos": gastos,
        "neto": ingresos - gastos
    }


def obtener_gastos_por_categoria(fecha_inicio, fecha_fin, limite=5):
    """Obtiene los gastos agrupados por categoría, ordenados de mayor a menor"""
    resultado = db.session.query(
        Categoria.id,
        Categoria.nombre,
        Categoria.color,
        Categoria.icono,
        func.sum(Movimiento.monto).label("total")
    ).join(Movimiento).filter(
        Categoria.tipo == "gasto",
        Movimiento.fecha >= fecha_inicio,
        Movimiento.fecha <= fecha_fin
    ).group_by(Categoria.id).order_by(func.sum(Movimiento.monto).desc()).limit(limite).all()

    return [
        {
            "id": r.id,
            "nombre": r.nombre,
            "color": r.color,
            "icono": r.icono,
            "total": r.total
        }
        for r in resultado
    ]


def obtener_ingresos_por_categoria(fecha_inicio, fecha_fin):
    """Obtiene los ingresos agrupados por categoría"""
    resultado = db.session.query(
        Categoria.id,
        Categoria.nombre,
        Categoria.color,
        Categoria.icono,
        func.sum(Movimiento.monto).label("total")
    ).join(Movimiento).filter(
        Categoria.tipo == "ingreso",
        Movimiento.fecha >= fecha_inicio,
        Movimiento.fecha <= fecha_fin
    ).group_by(Categoria.id).order_by(func.sum(Movimiento.monto).desc()).all()

    return [
        {
            "id": r.id,
            "nombre": r.nombre,
            "color": r.color,
            "icono": r.icono,
            "total": r.total
        }
        for r in resultado
    ]


def calcular_tasa_ahorro(fecha_inicio, fecha_fin):
    """Calcula el porcentaje de ingresos que se ahorraron"""
    flujo = calcular_flujo_periodo(fecha_inicio, fecha_fin)
    if flujo["ingresos"] == 0:
        return 0
    return (flujo["neto"] / flujo["ingresos"]) * 100


def obtener_tendencia_semanal(semanas=8):
    """Obtiene la tendencia de ingresos/gastos de las últimas N semanas"""
    hoy = date.today()
    tendencia = []

    for i in range(semanas - 1, -1, -1):
        # Calcular inicio de cada semana
        dias_atras = i * 7 + hoy.weekday()
        inicio_semana = hoy - timedelta(days=dias_atras)
        fin_semana = inicio_semana + timedelta(days=6)

        flujo = calcular_flujo_periodo(inicio_semana, fin_semana)
        tendencia.append({
            "semana": inicio_semana.strftime("%d/%m"),
            "ingresos": flujo["ingresos"],
            "gastos": flujo["gastos"],
            "neto": flujo["neto"]
        })

    return tendencia


def proyectar_balance(semanas_futuras=4):
    """Proyecta el balance futuro basado en el promedio de las últimas semanas"""
    # Obtener promedio semanal de las últimas 4 semanas
    tendencia = obtener_tendencia_semanal(4)
    if not tendencia:
        return []

    promedio_neto = sum(s["neto"] for s in tendencia) / len(tendencia)
    balance_actual = calcular_balance_total()

    proyeccion = []
    hoy = date.today()

    for i in range(1, semanas_futuras + 1):
        fecha_futura = hoy + timedelta(weeks=i)
        balance_proyectado = balance_actual + (promedio_neto * i)
        proyeccion.append({
            "semana": fecha_futura.strftime("%d/%m"),
            "balance": balance_proyectado
        })

    return proyeccion


def obtener_resumen_dashboard():
    """Genera todos los datos necesarios para el dashboard"""
    hoy = date.today()
    inicio_semana, fin_semana = obtener_rango_semana_actual()
    inicio_mes, fin_mes = obtener_rango_mes_actual()

    flujo_semana = calcular_flujo_periodo(inicio_semana, fin_semana)
    flujo_mes = calcular_flujo_periodo(inicio_mes, fin_mes)

    return {
        "fecha_actual": hoy,
        "balance_total": calcular_balance_total(),
        "flujo_semana": flujo_semana,
        "flujo_mes": flujo_mes,
        "tasa_ahorro_mes": calcular_tasa_ahorro(inicio_mes, fin_mes),
        "top_gastos_mes": obtener_gastos_por_categoria(inicio_mes, fin_mes, limite=5),
        "tendencia": obtener_tendencia_semanal(8),
        "proyeccion": proyectar_balance(4),
        "cuentas": [
            {"nombre": c.nombre, "tipo": c.tipo, "saldo": c.saldo_actual}
            for c in Cuenta.query.filter_by(activa=True).all()
        ]
    }
