"""Estrategia del Sprint 4: la penalización evalúa solo viabilidad financiera."""
import random
from motor_sprint4 import calcular_riesgo_difuso
from riesgo import VERSION_MOTOR

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

def crear_individuo(cliente):
    monto_original = cliente["monto_credito"]
    meses_original = round(cliente["plazo"] * 12)
    monto = random.uniform(monto_original * 0.70, monto_original)
    meses = random.randint(meses_original, 240)
    return [monto, meses / 12]

def crear_poblacion(cliente, tamaño=20):

    poblacion = []

    for i in range(tamaño):

        individuo = crear_individuo(
            cliente
        )

        poblacion.append(
            individuo
        )

    return poblacion

def calcular_fitness(individuo, cliente):
    monto, plazo = individuo
    monto_original = cliente["monto_credito"]
    plazo_original = cliente["plazo"]
    cuota = calcular_cuota(monto, plazo, cliente["tasa_anual"])
    capacidad = max(0, min(1, 1 - cuota / cliente["ingreso_mensual"]))
    cercania_monto = max(0, min(1, monto / monto_original))
    if plazo_original == 20:
        cercania_plazo = 1
    else:
        cercania_plazo = max(0, min(1, 1 - (plazo - plazo_original) / (20 - plazo_original)))

    # La revisión personal no invalida financieramente una oferta.
    oferta = cliente.copy()
    oferta["monto_credito"] = monto
    oferta["plazo"] = plazo
    indice = calcular_riesgo_difuso(oferta)
    penalizacion = 0 if indice <= 35 else 1
    return (0.50 * capacidad + 0.25 * cercania_monto
            + 0.25 * cercania_plazo - penalizacion)

def calcular_intereses_totales(monto, plazo, tasa_anual):

    cuota = calcular_cuota(
        monto, plazo, tasa_anual
    )

    meses = plazo * 12

    intereses = cuota * meses - monto

    return intereses

def utilidad_cliente(monto, plazo, cliente):

    monto_original = cliente["monto_credito"]
    plazo_original = cliente["plazo"]
    tasa_anual = cliente["tasa_anual"]

    cercania_monto = monto / monto_original

    if plazo_original == 20:
        cercania_plazo = 1
    else:
        cercania_plazo = 1 - (
            (plazo - plazo_original)
            / (20 - plazo_original)
        )

    intereses = calcular_intereses_totales(
        monto, plazo, tasa_anual
    )

    intereses_referencia = calcular_intereses_totales(
        monto_original, 20, tasa_anual
    )

    if intereses_referencia == 0:
        conveniencia_intereses = 1
    else:
        conveniencia_intereses = 1 - (
            intereses / intereses_referencia
        )

    conveniencia_intereses = max(
        0, min(1, conveniencia_intereses)
    )

    utilidad = (
        0.40 * cercania_monto
        + 0.30 * cercania_plazo
        + 0.30 * conveniencia_intereses
    )

    return utilidad

def utilidad_prestamista(monto, plazo, cliente):

    tasa_anual = cliente["tasa_anual"]
    ingreso = cliente["ingreso_mensual"]
    monto_original = cliente["monto_credito"]

    cuota = calcular_cuota(
        monto, plazo, tasa_anual
    )

    relacion = cuota / ingreso

    capacidad = 1 - relacion
    capacidad = max(0, min(1, capacidad))

    intereses = calcular_intereses_totales(
        monto, plazo, tasa_anual
    )

    intereses_referencia = calcular_intereses_totales(
        monto_original, 20, tasa_anual
    )

    if intereses_referencia == 0:
        ingresos_intereses = 0
    else:
        ingresos_intereses = (
            intereses / intereses_referencia
        )

    ingresos_intereses = max(
        0, min(1, ingresos_intereses)
    )

    utilidad = (
        0.60 * capacidad
        + 0.40 * ingresos_intereses
    )

    return utilidad

def mutar(individuo, cliente):
    hijo = individuo.copy()
    hijo[0] += random.uniform(-0.05, 0.05) * cliente["monto_credito"]
    meses = round(hijo[1] * 12) + random.randint(-6, 6)
    hijo[1] = meses / 12
    return hijo

def reparar(individuo, cliente):
    monto_original = cliente["monto_credito"]
    individuo[0] = max(monto_original * 0.70, min(monto_original, individuo[0]))
    meses_original = round(cliente["plazo"] * 12)
    meses = max(meses_original, min(240, round(individuo[1] * 12)))
    individuo[1] = meses / 12
    return individuo

def estrategia_evolutiva(
    cliente,
    mu=6,
    lambda_=12,
    generaciones=50
):

    historial_fitness = []

    # Crear población inicial

    poblacion = crear_poblacion(
        cliente,
        tamaño=mu
    )

    # Proceso evolutivo

    for generacion in range(
        generaciones
    ):

        # Ordenar la población de mayor a menor fitness

        poblacion.sort(
            key=lambda individuo:
            calcular_fitness(
                individuo,
                cliente
            ),
            reverse=True
        )

        # Seleccionar los mejores padres

        padres = (
            poblacion[:mu]
        )

        # Crear descendientes

        descendientes = []

        for i in range(
            lambda_
        ):

            padre = random.choice(
                padres
            )

            hijo = mutar(
                padre,
                cliente
            )

            hijo = reparar(
                hijo,
                cliente
            )

            descendientes.append(
                hijo
            )

        # Juntar padres y descendientes

        candidatos = (
            padres
            + descendientes
        )

        # Ordenar candidatos de mayor a menor fitness

        candidatos.sort(
            key=lambda individuo:
            calcular_fitness(
                individuo,
                cliente
            ),
            reverse=True
        )

        # Sobreviven los mejores individuos

        poblacion = (
            candidatos[:mu]
        )

        # Guardar el mejor fitness de la generación

        mejor_fitness_generacion = (
            calcular_fitness(
                poblacion[0],
                cliente
            )
        )

        historial_fitness.append(
            mejor_fitness_generacion
        )

    # Seleccionar el mejor individuo final

    mejor_individuo = (
        poblacion[0]
    )

    mejor_fitness = (
        calcular_fitness(
            mejor_individuo,
            cliente
        )
    )

    return (
        mejor_individuo,
        mejor_fitness,
        historial_fitness
    )
