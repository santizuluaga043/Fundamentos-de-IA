import math
import random
import unittest
from riesgo import evaluar_riesgo, motor_inferencia, decision_por_riesgo
from evolucion import calcular_cuota, estrategia_evolutiva, utilidad_cliente, utilidad_prestamista

BASE = dict(nombre='Prueba',edad=30,ingreso_mensual=4000000,monto_credito=40000000,plazo=3,tasa_anual=18,score=700,endeudamiento=40,antiguedad_empleo_actual=4,reportes_negativos=0)

class ModeloTest(unittest.TestCase):
    def test_umbrales(self):
        for x, d in [(35,'APROBADO'),(35.00001,'REVISIÓN'),(64.99999,'REVISIÓN'),(65,'RECHAZADO')]:
            self.assertEqual(decision_por_riesgo(x),d)
    def test_perfiles(self):
        self.assertEqual(motor_inferencia(dict(BASE,score=900,endeudamiento=10,monto_credito=1000000))[0],'APROBADO')
        self.assertEqual(motor_inferencia(dict(BASE,reportes_negativos=2))[0],'RECHAZADO')
        self.assertEqual(motor_inferencia(BASE)[0],'REVISIÓN')
        self.assertEqual(len(motor_inferencia(BASE)),2)
    def test_validacion(self):
        for campo, valor in [('ingreso_mensual',0),('plazo',0),('plazo',.12),('score',float('nan')),('reportes_negativos',.5)]:
            with self.assertRaises(ValueError): evaluar_riesgo(dict(BASE,**{campo:valor}))
    def test_cuota(self):
        self.assertEqual(calcular_cuota(1200,1,0),100)
        self.assertGreater(calcular_cuota(1200,1,18),100)
    def test_evolucion(self):
        random.seed(42)
        ind, fitness, hist=estrategia_evolutiva(BASE)
        self.assertEqual(len(hist),50)
        self.assertTrue(all(a<=b+1e-12 for a,b in zip(hist,hist[1:])))
        self.assertTrue(.7*BASE['monto_credito']<=ind[0]<=BASE['monto_credito'])
        self.assertTrue(BASE['plazo']<=ind[1]<=20)
        self.assertAlmostEqual(ind[1]*12,round(ind[1]*12))
        self.assertTrue(math.isfinite(fitness))
        for f in [utilidad_cliente,utilidad_prestamista]: self.assertTrue(0<=f(*ind,BASE)<=1)
    def test_plazo_maximo_sin_interes(self):
        random.seed(1)
        c=dict(BASE,plazo=20,tasa_anual=0)
        ind,_,_=estrategia_evolutiva(c,generaciones=2)
        self.assertEqual(ind[1],20)
        self.assertTrue(math.isfinite(utilidad_cliente(*ind,c)))

if __name__=='__main__': unittest.main()
