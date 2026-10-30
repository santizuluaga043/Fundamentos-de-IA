import unittest
from streamlit.testing.v1 import AppTest

class AppTestCase(unittest.TestCase):
    def abrir(self):
        at = AppTest.from_file('app.py', default_timeout=30).run()
        self.assertEqual(len(at.exception), 0)
        return at

    def test_evaluar_y_navegar(self):
        at = self.abrir()
        self.assertTrue(any(m.value == 'REVISIÓN' for m in at.metric))
        self.assertFalse(any(m.label == 'Monto alternativo' for m in at.metric))
        at.button[0].click().run()
        self.assertEqual(len(at.exception), 0)
        self.assertTrue(any(m.label == 'Monto alternativo' for m in at.metric))
        at.toggle(key='convergencia').set_value(True).run()
        at.toggle(key='trazabilidad').set_value(True).run()
        self.assertEqual(len(at.exception), 0)
        for page in ['Cómo funciona', 'Proyecto y herramientas']:
            at.sidebar.radio[0].set_value(page).run()
            self.assertEqual(len(at.exception), 0)

    def test_precision_y_oferta_obsoleta(self):
        at = self.abrir()
        at.button[0].click().run()
        riesgo = at.metric[1].value
        at.number_input(key='deuda').set_value(42.75).run()
        self.assertEqual(at.number_input(key='deuda').value, 42.75)
        self.assertNotEqual(at.metric[1].value, riesgo)
        self.assertNotIn('contraoferta', at.session_state)
        self.assertFalse(any(m.label == 'Monto alternativo' for m in at.metric))
        at.number_input(key='score').set_value(701).run()
        self.assertEqual(at.number_input(key='score').value, 701)
        self.assertEqual(len(at.slider), 0)
        self.assertEqual(len(at.exception), 0)

    def test_temas_y_decisiones(self):
        at = self.abrir()
        for tema in ['Oscuro', 'Claro', 'Automático']:
            at.sidebar.selectbox[0].set_value(tema).run()
            self.assertEqual(len(at.exception), 0)
        at.number_input(key='score').set_value(1000).run()
        at.number_input(key='deuda').set_value(0.).run()
        monto = next(n for n in at.number_input if n.label == 'Monto solicitado (COP)')
        monto.set_value(1000000.).run()
        self.assertEqual(at.metric[0].value, 'APROBADO')
        reportes = next(n for n in at.number_input if n.label == 'Reportes negativos')
        reportes.set_value(2).run()
        self.assertEqual(at.metric[0].value, 'RECHAZADO')
        self.assertEqual(len(at.button), 0)
