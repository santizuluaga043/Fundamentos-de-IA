"""Adaptador del Sprint 4 al contrato de datos de la interfaz existente."""
import math
from motor_sprint4 import (
    calcular_riesgo_difuso, calcular_cuota, evaluar_estabilidad_actual,
    fuzzificar_score, fuzzificar_endeudamiento, fuzzificar_capacidad,
    reglas as REGLAS, motor_inferencia as motor_notebook,
)

VERSION_MOTOR = 'sprint4-mamdani-v2-capacidad'

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



def decision_por_riesgo(r):
    return 'APROBADO' if r <= 35 else 'RECHAZADO' if r >= 65 else 'REVISIÓN'


def evaluar_riesgo(cliente):
    validar_cliente(cliente)
    indice = calcular_riesgo_difuso(cliente)
    decision, explicacion = motor_notebook(cliente)
    cuota = calcular_cuota(cliente['monto_credito'], cliente['plazo'], cliente['tasa_anual'])
    relacion = cuota / cliente['ingreso_mensual'] * 100
    score = fuzzificar_score(cliente['score'])
    deuda = fuzzificar_endeudamiento(cliente['endeudamiento'])
    capacidad = fuzzificar_capacidad(relacion)
    membresias = {
        'Score (malo → bueno)': tuple(float(v) for v in score.values()),
        'Endeudamiento (bajo → alto)': tuple(float(v) for v in deuda.values()),
        'Cuota / ingreso (baja → alta)': tuple(float(v) for v in capacidad.values()),
    }
    niveles = {'BAJO': 0, 'MEDIO': 1, 'ALTO': 2}
    reglas = [dict(score=niveles[s], deuda=niveles[d], cuota=niveles[c],
                   activacion=float(min(score[s], deuda[d], capacidad[c])), salida=salida)
              for s, d, c, salida in REGLAS]
    estabilidad = evaluar_estabilidad_actual(cliente['antiguedad_empleo_actual'], cliente['edad'])
    motivos = []
    if estabilidad in ('MEDIA', 'BAJA'):
        motivos.append('estabilidad laboral')
    if cliente['reportes_negativos'] == 1:
        motivos.append('un reporte negativo')
    revision_manual = bool(motivos)
    if revision_manual:
        explicacion += ' Requiere revisión personal de un funcionario por ' + ' y '.join(motivos) + '.'
    # Aislar la cuota: el mismo perfil debe aprobar financieramente con una
    # carga baja (<=15 %). Es diagnóstico, no una oferta ni otra búsqueda.
    perfil_cuota_baja = dict(cliente, monto_credito=cliente['monto_credito'] * (1. if relacion <= 15 else 15. / relacion))
    riesgo_cuota_baja = calcular_riesgo_difuso(perfil_cuota_baja)
    ejecutar = (decision == 'REVISIÓN' and 35 < indice < 65
                and not revision_manual and cliente['reportes_negativos'] == 0
                and riesgo_cuota_baja <= 35)
    if revision_manual:
        bloqueo = 'La revisión corresponde a ' + ' y '.join(motivos) + '. Requiere validación de un funcionario; cambiar el monto o el plazo no resuelve esa condición.'
    elif riesgo_cuota_baja > 35:
        bloqueo = 'El score y el endeudamiento impiden alcanzar la aprobación aun con una cuota baja. La contraoferta no está disponible para este perfil.'
    else:
        bloqueo = 'La contraoferta solo está disponible para solicitudes en revisión por capacidad de pago.'
    return dict(riesgo=indice, base=indice, decision=decision, explicacion=explicacion,
                cuota=cuota, relacion=relacion, membresias=membresias, reglas=reglas,
                estabilidad=estabilidad, revision_manual=revision_manual,
                motivos_revision=motivos, decision_financiera=decision_por_riesgo(indice),
                viable_financieramente=indice <= 35,
                ejecutar_evolutiva=ejecutar, riesgo_con_cuota_baja=riesgo_cuota_baja,
                motivo_bloqueo_contraoferta=None if ejecutar else bloqueo)


def motor_inferencia(cliente):
    r = evaluar_riesgo(cliente)
    return r['decision'], r['explicacion']
