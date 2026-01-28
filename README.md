# Finanzas Personales

Aplicacion web personal para el registro, almacenamiento, visualizacion y analisis de finanzas personales.

## Caracteristicas

- **Dashboard semanal**: Vista principal con resumen de balance, flujo y tendencias
- **Registro de movimientos**: CRUD completo para ingresos y gastos
- **Categorias flexibles**: Sistema de categorias con soporte para subcategorias
- **Reportes por periodo**: Analisis detallado de cualquier rango de fechas
- **Proyecciones simples**: Estimacion de balance futuro basado en tendencias

## Requisitos

- Python 3.8+
- pip

## Instalacion

1. Clonar el repositorio:
```bash
git clone <url-del-repo>
cd app_financiero
```

2. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o en Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Ejecutar la aplicacion:
```bash
python run.py
```

5. Abrir en el navegador: http://localhost:5000

## Estructura del Proyecto

```
app_financiero/
├── app/
│   ├── __init__.py          # Factory de la aplicacion
│   ├── models.py            # Modelos de datos
│   ├── routes/
│   │   ├── movimientos.py   # CRUD de transacciones
│   │   ├── categorias.py    # Gestion de categorias
│   │   └── reportes.py      # Dashboard y reportes
│   ├── services/
│   │   └── analisis.py      # Logica de calculos financieros
│   ├── templates/           # Templates HTML (Jinja2)
│   └── static/              # CSS y JS
├── data/                    # Base de datos SQLite
├── tests/                   # Tests
├── config.py                # Configuracion
├── requirements.txt         # Dependencias
└── run.py                   # Punto de entrada
```

## Uso

### Flujo de trabajo semanal

1. Acceder al **Dashboard** para ver el estado actual
2. Registrar **Movimientos** de la semana (ingresos y gastos)
3. Revisar **Reportes** para analizar patrones de gasto
4. Ajustar **Categorias** segun sea necesario

### Metricas principales

- **Balance total**: Suma de todas las cuentas activas
- **Flujo semanal/mensual**: Diferencia entre ingresos y gastos
- **Tasa de ahorro**: Porcentaje de ingresos no gastados
- **Top gastos**: Categorias con mayor gasto
- **Proyeccion**: Estimacion de balance futuro

## Tecnologias

- **Backend**: Flask + SQLAlchemy
- **Base de datos**: SQLite
- **Frontend**: Jinja2 + Pico CSS + Chart.js
- **Sin dependencias de JavaScript frameworks**

## Licencia

Uso personal.
