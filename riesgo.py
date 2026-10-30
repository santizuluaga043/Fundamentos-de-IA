"""FIS Sugeno de orden cero: 27 reglas, AND producto y media ponderada."""
import math
from itertools import product


def validar_cliente(c):
    campos = ('edad', 'ingreso_mensual', 'monto_credito', 'plazo', 'tasa_anual',
              'score', 'endeudamiento', 'antiguedad_empleo_actual', 'reportes_negativos')
    for k in campos:
        if not isinstance(c.get(k), (int, float)) or not math.isfinite(c[k]):
            raise ValueError(f'{k}: se requiere un número finito.')
    if c['ingreso_mensual'] <= 0 or c['monto_credito'] <= 0:
        raise ValueError('Ingreso y monto deben ser positivos.')
    if not 0 < c['plazo'] <= 20 or not math.isclose(c['plazo']*12, round(c['plazo']*12), abs_tol=1e-8):
        raise ValueError('Plazo: de 1 a 240 meses completos.')
    if not 0 <= c['score'] <= 1000 or not 0 <= c['endeudamiento'] <= 100:
        raise ValueError('Score: 0–1000; endeudamiento: 0–100 %.')
    if not 18 <= c['edad'] <= 100 or c['edad'] != int(c['edad']):
        raise ValueError('Edad: entero entre 18 y 100.')
    if c['tasa_anual'] < 0 or c['antiguedad_empleo_actual'] < 0 or c['reportes_negativos'] < 0:
        raise ValueError('Tasa, antigüedad y reportes no pueden ser negativos.')
    if c['reportes_negativos'] != int(c['reportes_negativos']):
        raise ValueError('Los reportes deben ser enteros.')


def pertenencias(x, a, b, c):
    """Partición continua con hombros y triángulo; suma siempre uno."""
    bajo = max(0., min(1., (b-x)/(b-a)))
    alto = max(0., min(1., (x-b)/(c-b)))
    return (bajo, max(0., 1-bajo-alto), alto)


def decision_por_riesgo(r):
    return 'APROBADO' if r <= 35 else 'RECHAZADO' if r >= 65 else 'REVISIÓN'


def evaluar_riesgo(cliente):
    validar_cliente(cliente)
    # Importación local evita dependencia circular al conservar Sprint 3.
    from evolucion import calcular_cuota, evaluar_estabilidad_actual
    c = cliente
    cuota = calcular_cuota(c['monto_credito'], c['plazo'], c['tasa_anual'])
    relacion = cuota / c['ingreso_mensual'] * 100
    membresias = {
        'Score (malo → bueno)': pertenencias(c['score'], 500, 650, 800),
        'Endeudamiento (bajo → alto)': pertenencias(c['endeudamiento'], 30, 50, 70),
        'Cuota / ingreso (baja → alta)': pertenencias(relacion, 20, 30, 40),
    }
    reglas = []
    for s, d, p in product(range(3), repeat=3):
        activacion = membresias['Score (malo → bueno)'][s] * membresias['Endeudamiento (bajo → alto)'][d] * membresias['Cuota / ingreso (baja → alta)'][p]
        # Consecuentes constantes: perfil favorable 10, intermedio 50, adverso 90.
        consecuente = 10 + 40 * (.35*(2-s) + .25*d + .40*p)
        reglas.append({'score': s, 'deuda': d, 'cuota': p, 'activacion': activacion, 'consecuente': consecuente})
    base = sum(r['activacion']*r['consecuente'] for r in reglas) / sum(r['activacion'] for r in reglas)
    estabilidad = evaluar_estabilidad_actual(c['antiguedad_empleo_actual'], c['edad'])
    ajuste = {'ESTABLE': 0, 'N/A': 0, 'MEDIA': 5, 'BAJA': 10}[estabilidad]
    riesgo = min(100., base + ajuste + (10 if c['reportes_negativos'] == 1 else 0))
    # Se conserva la regla de rechazo por >=2 reportes del sistema experto.
    if c['reportes_negativos'] >= 2:
        riesgo = max(65., riesgo)
    explicacion = (f'Riesgo global {riesgo:.2f}/100; base difusa {base:.2f}, '
                   f'estabilidad {estabilidad} (+{ajuste}), reportes {c["reportes_negativos"]}. '
                   f'Cuota/ingreso: {relacion:.1f} %. '
                   'Umbrales: aprobación ≤35; rechazo ≥65; revisión entre ambos.')
    return {'riesgo': riesgo, 'base': base, 'decision': decision_por_riesgo(riesgo),
            'explicacion': explicacion, 'cuota': cuota, 'relacion': relacion,
            'membresias': membresias, 'reglas': reglas, 'estabilidad': estabilidad}


def motor_inferencia(cliente):
    r = evaluar_riesgo(cliente)
    return r['decision'], r['explicacion']
