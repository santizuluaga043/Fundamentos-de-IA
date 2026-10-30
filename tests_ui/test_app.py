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
        self.assertEqual(len(at.toggle), 0)
        at.sidebar.radio[0].set_value('Cómo funciona').run()
        self.assertTrue(any(h.value == 'Cálculos de la última alternativa' for h in at.subheader))
        self.assertTrue(any('Fitness' in str(t.value) for t in at.table))
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

    def test_marca_indice_y_bienvenida(self):
        at = self.abrir()
        html = '\n'.join(m.value for m in at.markdown)
        for destino in ['perfil', 'resultado', 'explicacion', 'alternativa', 'comparacion']:
            self.assertIn(f'href="#{destino}"', html)
            self.assertIn(f'id="{destino}"', html)
        self.assertIn('cl-intro', html)
        self.assertIn('Credi', html)
        at.number_input(key='score').set_value(720).run()
        self.assertFalse(any('class="cl-welcome cl-intro"' in m.value for m in at.markdown))
        self.assertFalse(any('Grados de pertenencia' in m.value for m in at.markdown))

    def test_perfil_persiste_entre_paginas(self):
        at = self.abrir()
        at.number_input(key='deuda').set_value(42.75).run()
        at.number_input(key='score').set_value(712).run()
        at.button[0].click().run()
        at.sidebar.radio[0].set_value('Cómo funciona').run()
        at.sidebar.radio[0].set_value('Evaluar solicitud').run()
        self.assertEqual(at.number_input(key='deuda').value, 42.75)
        self.assertEqual(at.number_input(key='score').value, 712)
        self.assertIn('contraoferta', at.session_state)
        self.assertEqual(len(at.exception), 0)
