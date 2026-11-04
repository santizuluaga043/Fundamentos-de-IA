"""Comparación independiente con las funciones del notebook, sin ejecutar su main."""
import ast
import json
import random
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from riesgo import evaluar_riesgo, motor_inferencia
from evolucion import calcular_fitness, estrategia_evolutiva
from motor_sprint4 import reglas

BASE = dict(nombre='Prueba',edad=30,ingreso_mensual=4000000,monto_credito=40000000,plazo=3,tasa_anual=18,score=700,endeudamiento=40,antiguedad_empleo_actual=4,reportes_negativos=0)


def referencia():
    nb = json.loads((Path(__file__).parents[1]/'notebooks/Sprint-4.ipynb').read_text())
    tree = ast.parse(''.join(nb['cells'][0]['source']))
    body = []
    for n in tree.body:
        if isinstance(n, ast.FunctionDef) and n.name not in {'ingresar_datos','mostrar_resultado','mostrar_contraoferta','graficar_convergencia'}:
            body.append(n)
        elif isinstance(n, ast.Assign) and any(isinstance(t,ast.Name) and t.id in {'universo','riesgo','reglas'} for t in n.targets):
            body.append(n)
    ns = dict(np=np,random=random)
    exec(compile(ast.Module(body=body,type_ignores=[]),'<notebook-reference>','exec'), ns)
    return ns


class Sprint4Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ref = referencia()

    def test_27_reglas_exactas(self):
        self.assertEqual(reglas, self.ref['reglas'])
        self.assertEqual(len(reglas),27)
        self.assertEqual(len(set(r[:3] for r in reglas)),27)

    def test_coincidencia_motor_y_riesgo(self):
        rng = random.Random(412)
        perfiles = [dict(BASE,score=s,endeudamiento=d,monto_credito=m,reportes_negativos=n,antiguedad_empleo_actual=a)
                    for s,d,m,n,a in [(0,0,1,0,4),(1000,100,1e9,2,0),(900,10,1e6,1,1),(700,40,4e7,0,4)]]
        for _ in range(100):
            perfiles.append(dict(BASE,score=rng.randint(0,1000),endeudamiento=rng.uniform(0,100),monto_credito=rng.uniform(1,1e8),plazo=rng.randint(1,240)/12, reportes_negativos=rng.randint(0,2),antiguedad_empleo_actual=rng.choice([0,2,4])))
        for c in perfiles:
            with self.subTest(c=c):
                r = evaluar_riesgo(c)
                self.assertAlmostEqual(r['riesgo'],self.ref['calcular_riesgo_difuso'](c),places=10)
                d,e = self.ref['motor_inferencia'](c)
                self.assertEqual(r['decision'],d)
                self.assertTrue(r['explicacion'].startswith(e))
                self.assertEqual(motor_inferencia(c),(d,r['explicacion']))

    def test_revision_manual_no_altera_riesgo_ni_fitness(self):
        c = dict(BASE,score=900,endeudamiento=10,monto_credito=1000000)
        base = evaluar_riesgo(c)
        for cambios in [dict(reportes_negativos=1),dict(antiguedad_empleo_actual=1),dict(reportes_negativos=1,antiguedad_empleo_actual=2)]:
            manual = dict(c,**cambios); r = evaluar_riesgo(manual)
            self.assertEqual(r['decision'],'REVISIÓN')
            self.assertTrue(r['revision_manual'])
            self.assertFalse(r['ejecutar_evolutiva'])
            self.assertIn('funcionario',r['explicacion'])
            self.assertEqual(r['riesgo'],base['riesgo'])
            self.assertEqual(calcular_fitness([c['monto_credito'],c['plazo']],manual),calcular_fitness([c['monto_credito'],c['plazo']],c))

    def test_fitness_y_evolucion_con_excepcion_solicitada(self):
        # La única divergencia intencional del fitness del notebook: aprobación
        # exclusivamente financiera para no penalizar la validación personal.
        ref = referencia()
        ref['motor_inferencia'] = lambda c: ('APROBADO' if ref['calcular_riesgo_difuso'](c)<=35 else 'REVISIÓN','')
        c = dict(BASE,score=900,endeudamiento=20,reportes_negativos=1,antiguedad_empleo_actual=1)
        self.assertFalse(evaluar_riesgo(c)['ejecutar_evolutiva'])
        random.seed(42); esperado = ref['estrategia_evolutiva'](c)
        random.seed(42); actual = estrategia_evolutiva(c)
        self.assertEqual(actual,esperado)
        oferta=dict(c,monto_credito=actual[0][0],plazo=actual[0][1])
        r=evaluar_riesgo(oferta)
        self.assertTrue(r['viable_financieramente'])
        self.assertTrue(r['revision_manual'])
        self.assertEqual(r['decision'],'REVISIÓN')
        self.assertGreater(actual[1],0)

    def test_umbrales_de_activacion(self):
        for indice, ejecutar in [(35,False),(35.0001,True),(64.9999,True),(65,False)]:
            with patch('riesgo.calcular_riesgo_difuso',side_effect=[indice,15.5]):
                self.assertEqual(evaluar_riesgo(BASE)['ejecutar_evolutiva'],ejecutar)

    def test_rechazo_prevalece_sobre_revision_manual(self):
        for c in [dict(BASE,score=400,endeudamiento=90,monto_credito=80000000,reportes_negativos=1),dict(BASE,score=900,endeudamiento=10,monto_credito=1e6,reportes_negativos=2)]:
            self.assertEqual(evaluar_riesgo(c)['decision'],'RECHAZADO')

    def test_extremos_y_ausencia_de_reglas(self):
        for cambios in [dict(score=1000,monto_credito=1000000,endeudamiento=10),dict(endeudamiento=100),dict(monto_credito=1e10)]:
            c=dict(BASE,**cambios)
            r=evaluar_riesgo(c)
            self.assertAlmostEqual(r['riesgo'],self.ref['calcular_riesgo_difuso'](c),places=10)
            self.assertEqual(r['decision'],'APROBADO' if c['score']==1000 else 'RECHAZADO')
        with patch('motor_sprint4.reglas',[]):
            with self.assertRaisesRegex(ValueError,'No se activó ninguna regla difusa'):
                evaluar_riesgo(BASE)
        ref=referencia();ref['reglas']=[]
        with self.assertRaisesRegex(ValueError,'No se activó ninguna regla difusa'):
            ref['calcular_riesgo_difuso'](BASE)

    def test_trapecios_escalares_y_vectores(self):
        from motor_sprint4 import trapmf
        for limites in [(0,0,20,40),(60,80,100,100),(0,0,100,100)]:
            valores=np.array([-1,0,20,40,60,80,100,101])
            np.testing.assert_allclose(trapmf(valores,*limites),self.ref['trapmf'](valores,*limites))
        self.assertEqual(float(trapmf(1000,700,800,1000,1000)),1.)
        self.assertEqual(float(trapmf(0,0,0,500,650)),1.)

    def test_busqueda_solo_por_capacidad(self):
        elegible=dict(BASE,score=900,endeudamiento=20)
        self.assertTrue(evaluar_riesgo(elegible)['ejecutar_evolutiva'])
        for cambios in [dict(reportes_negativos=1),dict(reportes_negativos=2),dict(antiguedad_empleo_actual=1),dict(score=400),dict(endeudamiento=60),dict(monto_credito=1000000)]:
            with self.subTest(cambios=cambios):
                r=evaluar_riesgo(dict(elegible,**cambios))
                self.assertFalse(r['ejecutar_evolutiva'])
                self.assertTrue(r['motivo_bloqueo_contraoferta'])
        self.assertFalse(evaluar_riesgo(BASE)['ejecutar_evolutiva'])
