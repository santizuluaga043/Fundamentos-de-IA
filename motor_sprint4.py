"""Motor Mamdani del notebook Sprint-4, sin entrada interactiva ni gráficos."""
import numpy as np

def evaluar_estabilidad_actual(antiguedad_actual, edad):

    if 17 <= edad <= 20:

        if antiguedad_actual >= 1:
            return "ESTABLE"

        else:
            return "N/A"

    elif 21 <= edad <= 24:

        if antiguedad_actual >= 1:
            return "ESTABLE"

        else:
            return "MEDIA"

    elif 25 <= edad <= 35:

        if antiguedad_actual >= 4:
            return "ESTABLE"

        elif antiguedad_actual >= 2:
            return "MEDIA"

        else:
            return "BAJA"

    elif 36 <= edad <= 50:

        if antiguedad_actual >= 6:
            return "ESTABLE"

        elif antiguedad_actual >= 4:
            return "MEDIA"

        else:
            return "BAJA"

    elif 51 <= edad <= 65:

        if antiguedad_actual >= 8:
            return "ESTABLE"

        elif antiguedad_actual >= 6:
            return "MEDIA"

        else:
            return "BAJA"

    else:
        return "N/A"

def convertir_tasa_mensual(tasa_anual):
    tasa_decimal = tasa_anual / 100
    tasa_mensual = (1 + tasa_decimal) ** (1 / 12) - 1
    return tasa_mensual

def calcular_cuota(monto_credito, plazo, tasa_anual):
    tasa_mensual = convertir_tasa_mensual(tasa_anual)
    meses = round(plazo * 12)
    if meses <= 0:
        raise ValueError("El plazo debe ser positivo.")
    if tasa_mensual == 0:
        return monto_credito / meses
    return monto_credito * tasa_mensual / (1 - (1 + tasa_mensual) ** (-meses))

def trimf(x, a, b, c):
    return np.interp(x, [a, b, c], [0, 1, 0])

def trapmf(x, a, b, c, d):
    x = np.asarray(x)

    resultado = np.interp(x, [a, b, c, d], [0, 1, 1, 0])

    if a == b:
        resultado = np.where(x <= b, 1, resultado)

    if c == d:
        resultado = np.where(x >= c, 1, resultado)

    return resultado

def fuzzificar_score(score):
    return {
        "BAJO": trapmf(score, 0, 0, 500, 650),
        "MEDIO": trimf(score, 550, 700, 800),
        "ALTO": trapmf(score, 700, 800, 1000, 1000)
    }

def fuzzificar_endeudamiento(deuda):
    return {
        "BAJO": trapmf(deuda, 0, 0, 25, 45),
        "MEDIO": trimf(deuda, 30, 50, 70),
        "ALTO": trapmf(deuda, 55, 75, 100, 100)
    }

def fuzzificar_capacidad(porcentaje):
    return {
        "BAJO": trapmf(porcentaje, 0, 0, 15, 25),
        "MEDIO": trimf(porcentaje, 15, 30, 45),
        "ALTO": trapmf(porcentaje, 35, 50, 100, 100)
    }

universo = np.linspace(0, 100, 1001)

riesgo = {
    "BAJO": trapmf(universo, 0, 0, 20, 40),
    "MEDIO": trimf(universo, 25, 50, 75),
    "ALTO": trapmf(universo, 60, 80, 100, 100)
}

reglas = [
    # Capacidad BAJA: cuota pequeña frente al ingreso
    ("BAJO", "BAJO", "BAJO", "MEDIO"),
    ("BAJO", "MEDIO", "BAJO", "ALTO"),
    ("BAJO", "ALTO", "BAJO", "ALTO"),
    ("MEDIO", "BAJO", "BAJO", "BAJO"),
    ("MEDIO", "MEDIO", "BAJO", "MEDIO"),
    ("MEDIO", "ALTO", "BAJO", "ALTO"),
    ("ALTO", "BAJO", "BAJO", "BAJO"),
    ("ALTO", "MEDIO", "BAJO", "BAJO"),
    ("ALTO", "ALTO", "BAJO", "ALTO"),

    # Capacidad MEDIA
    ("BAJO", "BAJO", "MEDIO", "ALTO"),
    ("BAJO", "MEDIO", "MEDIO", "ALTO"),
    ("BAJO", "ALTO", "MEDIO", "ALTO"),
    ("MEDIO", "BAJO", "MEDIO", "MEDIO"),
    ("MEDIO", "MEDIO", "MEDIO", "MEDIO"),
    ("MEDIO", "ALTO", "MEDIO", "ALTO"),
    ("ALTO", "BAJO", "MEDIO", "MEDIO"),
    ("ALTO", "MEDIO", "MEDIO", "MEDIO"),
    ("ALTO", "ALTO", "MEDIO", "ALTO"),

    # Capacidad ALTA: cuota grande frente al ingreso
    ("BAJO", "BAJO", "ALTO", "ALTO"),
    ("BAJO", "MEDIO", "ALTO", "ALTO"),
    ("BAJO", "ALTO", "ALTO", "ALTO"),
    ("MEDIO", "BAJO", "ALTO", "ALTO"),
    ("MEDIO", "MEDIO", "ALTO", "ALTO"),
    ("MEDIO", "ALTO", "ALTO", "ALTO"),
    ("ALTO", "BAJO", "ALTO", "ALTO"),
    ("ALTO", "MEDIO", "ALTO", "ALTO"),
    ("ALTO", "ALTO", "ALTO", "ALTO")
]

def calcular_riesgo_difuso(cliente):

    cuota = calcular_cuota(
        cliente["monto_credito"],
        cliente["plazo"],
        cliente["tasa_anual"]
    )

    porcentaje = cuota / cliente["ingreso_mensual"] * 100

    score = fuzzificar_score(cliente["score"])
    deuda = fuzzificar_endeudamiento(cliente["endeudamiento"])
    capacidad = fuzzificar_capacidad(porcentaje)

    agregado = np.zeros_like(universo)

    for s, d, c, salida in reglas:

        # Activación de la regla (operador Y)
        activacion = min(score[s], deuda[d], capacidad[c])

        # Recortar la salida de la regla
        recorte = np.minimum(activacion, riesgo[salida])

        # Combinar con las otras reglas
        agregado = np.maximum(agregado, recorte)

    # Centroide
    area = np.trapezoid(agregado, universo)

    if area == 0:
        raise ValueError("No se activó ninguna regla difusa.")

    indice = np.trapezoid(universo * agregado, universo) / area

    return float(indice)

def motor_inferencia(cliente):

    indice = calcular_riesgo_difuso(cliente)

    # Decisión según el índice de riesgo
    if indice <= 35:
        decision = "APROBADO"

    elif indice >= 65:
        decision = "RECHAZADO"

    else:
        decision = "REVISIÓN"

    explicacion = f"Índice de riesgo crediticio: {indice:.2f}/100."

    # Conservar restricciones importantes
    if cliente["reportes_negativos"] >= 2:
        decision = "RECHAZADO"
        explicacion += " Tiene dos o más reportes negativos."

    elif cliente["reportes_negativos"] == 1:
        if decision == "APROBADO":
            decision = "REVISIÓN"
        explicacion += " Tiene un reporte negativo."

    estabilidad = evaluar_estabilidad_actual(
        cliente["antiguedad_empleo_actual"],
        cliente["edad"]
    )

    if estabilidad in ["MEDIA", "BAJA"] and decision == "APROBADO":
        decision = "REVISIÓN"
        explicacion += " Requiere revisión de estabilidad laboral."

    return decision, explicacion
