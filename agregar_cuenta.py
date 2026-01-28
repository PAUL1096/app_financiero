#!/usr/bin/env python3
"""
Script para agregar nuevas cuentas a la base de datos existente.
Ejecutar: python agregar_cuenta.py
"""
import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, Cuenta

app = create_app()

def agregar_cuenta_tarjeta_credito():
    """Agrega la cuenta de Tarjeta de Crédito si no existe"""
    with app.app_context():
        # Verificar si ya existe
        cuenta_existente = Cuenta.query.filter_by(nombre="Tarjeta de Crédito").first()

        if cuenta_existente:
            print("La cuenta 'Tarjeta de Crédito' ya existe.")
            return

        # Crear la cuenta
        nueva_cuenta = Cuenta(
            nombre="Tarjeta de Crédito",
            tipo="tarjeta_credito",
            saldo_inicial=0.0,
            activa=True
        )

        db.session.add(nueva_cuenta)
        db.session.commit()

        print("Cuenta 'Tarjeta de Crédito' agregada exitosamente.")
        print("Tus datos existentes permanecen intactos.")

if __name__ == "__main__":
    agregar_cuenta_tarjeta_credito()
