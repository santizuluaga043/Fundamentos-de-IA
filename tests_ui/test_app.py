import unittest
from streamlit.testing.v1 import AppTest

class AppTestCase(unittest.TestCase):
    def test_evaluar_y_navegar(self):
        at=AppTest.from_file('app.py', default_timeout=30).run()
        self.assertEqual(len(at.exception),0)
        at.button[0].click().run()
        self.assertEqual(len(at.exception),0)
        self.assertTrue(any(m.value=='REVISIÓN' for m in at.metric))
        self.assertTrue(any(m.label=='Monto alternativo' for m in at.metric))
        for page in ['Cómo funciona','Proyecto y herramientas']:
            at.sidebar.radio[0].set_value(page).run()
            self.assertEqual(len(at.exception),0)
