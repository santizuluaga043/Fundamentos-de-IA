import unittest
from streamlit.testing.v1 import AppTest

class AppTestCase(unittest.TestCase):
    def abrir(self, capacidad=True):
        at = AppTest.from_file('app.py', default_timeout=30).run()
        if capacidad:
            at.number_input(key='score').set_value(900)
            at.number_input(key='deuda').set_value(20.)
            at.run()
        self.assertEqual(len(at.exception), 0)
        return at

    def test_evaluar_y_navegar(self):
        at = self.abrir()
        self.assertTrue(any(m.value == 'REVISIÓN' for m in at.metric))
        self.assertTrue(any(m.label == 'Monto alternativo' for m in at.metric))
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
        membresias_antes = at.session_state['evaluacion_actual']['membresias']['Endeudamiento (bajo → alto)']
        at.number_input(key='deuda').set_value(42.75).run()
        self.assertEqual(at.number_input(key='deuda').value, 42.75)
        self.assertNotEqual(at.session_state['evaluacion_actual']['membresias']['Endeudamiento (bajo → alto)'], membresias_antes)
        self.assertEqual(at.session_state['perfil_oferta']['endeudamiento'], 42.75)
        self.assertTrue(any(m.label == 'Monto alternativo' for m in at.metric))
        at.number_input(key='score').set_value(701).run()
        self.assertEqual(at.number_input(key='score').value, 701)
        self.assertNotIn('contraoferta', at.session_state)
        self.assertTrue(at.button[0].disabled)
        self.assertEqual(len(at.slider), 0)
        self.assertEqual(len(at.exception), 0)

    def test_temas_y_decisiones(self):
        at = self.abrir()
        for tema in ['Oscuro', 'Claro', 'Automático']:
            at.sidebar.selectbox[0].set_value(tema).run()
            self.assertEqual(len(at.exception), 0)
        at.number_input(key='score').set_value(900).run()
        at.number_input(key='deuda').set_value(0.).run()
        monto = next(n for n in at.number_input if n.label == 'Monto solicitado (COP)')
        monto.set_value(1000000.).run()
        self.assertEqual(at.metric[0].value, 'APROBADO')
        reportes = next(n for n in at.number_input if n.label == 'Reportes negativos')
        reportes.set_value(2).run()
        self.assertEqual(at.metric[0].value, 'RECHAZADO')
        self.assertEqual(len(at.button), 0)

    def test_marca_indice_y_bienvenida(self):
        at = self.abrir(capacidad=False)
        html = '\n'.join(m.value for m in at.markdown)
        for destino in ['perfil', 'resultado', 'explicacion', 'comparacion']:
            self.assertIn(f'href="#{destino}"', html)
            self.assertIn(f'id="{destino}"', html)
        self.assertIn('cl-intro', html)
        self.assertIn('Credi', html)
        at.number_input(key='score').set_value(720).run()
        self.assertFalse(any('class="cl-welcome cl-intro"' in m.value for m in at.markdown))
        self.assertFalse(any('Grados de pertenencia' in m.value for m in at.markdown))

    def test_perfil_persiste_entre_paginas(self):
        at = self.abrir()
        at.number_input(key='deuda').set_value(21.).run()
        at.number_input(key='score').set_value(912).run()
        at.button[0].click().run()
        at.sidebar.radio[0].set_value('Cómo funciona').run()
        at.sidebar.radio[0].set_value('Evaluar solicitud').run()
        self.assertEqual(at.number_input(key='deuda').value, 21.)
        self.assertEqual(at.number_input(key='score').value, 912)
        self.assertIn('contraoferta', at.session_state)
        self.assertEqual(len(at.exception), 0)

    def test_actualizacion_con_modulo_anterior_en_memoria(self):
        import importlib
        import interfaz
        # Reproducir una sesión anterior al despliegue de estilos_marca.
        del interfaz.estilos_marca
        try:
            at = self.abrir()
            self.assertTrue(any('Tu crédito, con claridad.' == t.value for t in at.title))
            self.assertTrue(callable(interfaz.estilos_marca))
        finally:
            importlib.reload(interfaz)

    def test_plazo_en_anios_y_conversion(self):
        from evolucion import calcular_cuota
        at = self.abrir()
        at.number_input(key='plazo_anios').set_value(3.5).run()
        self.assertEqual(len(at.exception), 0)
        self.assertTrue(any('42 meses' in c.value for c in at.caption))
        self.assertAlmostEqual(at.session_state['evaluacion_actual']['cuota'], calcular_cuota(40000000, 3.5, 18))
        at.sidebar.radio[0].set_value('Cómo funciona').run()
        at.sidebar.radio[0].set_value('Evaluar solicitud').run()
        self.assertEqual(at.number_input(key='plazo_anios').value, 3.5)
        at.number_input(key='plazo_anios').set_value(2.1).run()
        self.assertGreater(len(at.error), 0)
        self.assertEqual(len(at.metric), 0)

    def test_revision_personal_con_y_sin_busqueda(self):
        at = self.abrir()
        at.number_input(key='score').set_value(900).run()
        at.number_input(key='deuda').set_value(20.).run()
        at.number_input(key='reportes').set_value(1).run()
        at.number_input(key='antiguedad').set_value(1.).run()
        self.assertEqual(at.metric[0].value, 'REVISIÓN')
        self.assertFalse(at.session_state['evaluacion_actual']['ejecutar_evolutiva'])
        self.assertNotIn('contraoferta', at.session_state)
        self.assertTrue(at.button[0].disabled)
        self.assertTrue(any('Requiere revisión personal de un funcionario' in i.value for i in at.info))
        at.number_input(key='monto').set_value(1000000.).run()
        self.assertEqual(at.metric[0].value, 'REVISIÓN')
        self.assertFalse(at.session_state['evaluacion_actual']['ejecutar_evolutiva'])
        self.assertNotIn('contraoferta', at.session_state)
        self.assertTrue(at.button[0].disabled)
        self.assertEqual(len(at.exception),0)

    def test_una_ejecucion_por_perfil_y_una_grafica(self):
        from unittest.mock import patch
        import streamlit as st
        import evolucion
        st.cache_data.clear()
        with patch('evolucion.estrategia_evolutiva', wraps=evolucion.estrategia_evolutiva) as ejecutar:
            at=self.abrir()
            self.assertEqual(ejecutar.call_count,1)
            at.run()
            at.button[0].click().run()
            self.assertEqual(ejecutar.call_count,1)
            at.sidebar.radio[0].set_value('Cómo funciona').run()
            self.assertEqual(len(at.get('arrow_vega_lite_chart')),1)
            at.sidebar.radio[0].set_value('Evaluar solicitud').run()
            self.assertEqual(ejecutar.call_count,1)
        st.cache_data.clear()

    def test_actualizacion_invalida_backend_y_oferta_anteriores(self):
        import riesgo
        import evolucion
        from unittest.mock import patch
        at=self.abrir()
        at.session_state['version_motor']='sugeno-anterior'
        at.session_state['contraoferta']={'obsoleta':True}
        # Módulos sin marca: reproducir los ya importados antes del despliegue.
        del riesgo.VERSION_MOTOR
        del evolucion.VERSION_MOTOR
        at.run()
        self.assertEqual(len(at.exception),0)
        self.assertEqual(at.session_state['version_motor'],'sprint4-mamdani-v3-trapmf')
        self.assertNotIn('obsoleta',at.session_state['contraoferta'])
        self.assertEqual(evolucion.VERSION_MOTOR,riesgo.VERSION_MOTOR)

    def test_actualizacion_recarga_indice_visual(self):
        import importlib
        import marca
        del marca.indice
        try:
            at=self.abrir()
            self.assertTrue(any('class="cl-tip"' in m.value for m in at.markdown))
        finally:
            importlib.reload(marca)

    def test_riesgo_bajo_distingue_aprobacion_y_revision_personal(self):
        at=self.abrir()
        at.number_input(key='score').set_value(900).run()
        at.number_input(key='deuda').set_value(10.).run()
        at.number_input(key='monto').set_value(1000000.).run()
        self.assertEqual(at.metric[0].value,'APROBADO')
        for campo in ['antiguedad','reportes']:
            at.number_input(key=campo).set_value(1 if campo=='reportes' else 1.).run()
            self.assertLess(at.session_state['evaluacion_actual']['riesgo'],35)
            self.assertEqual(at.metric[0].value,'REVISIÓN')
            self.assertTrue(any('Evaluación financiera: APROBADO' in w.value and 'funcionario' in w.value for w in at.warning))
        at.number_input(key='reportes').set_value(2).run()
        self.assertEqual(at.metric[0].value,'RECHAZADO')
        self.assertTrue(any('por dos o más reportes negativos' in e.value for e in at.error))
        at.number_input(key='antiguedad').set_value(4.).run()
        at.number_input(key='reportes').set_value(0).run()
        self.assertEqual(at.metric[0].value,'APROBADO')
        self.assertEqual(len(at.exception),0)

    def test_revision_por_otros_factores_no_ejecuta_busqueda(self):
        from unittest.mock import patch
        import evolucion
        with patch('evolucion.estrategia_evolutiva', wraps=evolucion.estrategia_evolutiva) as buscar:
            at=self.abrir(capacidad=False)
            self.assertEqual(at.metric[0].value,'REVISIÓN')
            self.assertTrue(at.button[0].disabled)
            self.assertTrue(any('score y el endeudamiento' in i.value for i in at.info))
            self.assertEqual(buscar.call_count,0)
            at.number_input(key='reportes').set_value(1).run()
            self.assertTrue(at.button[0].disabled)
            self.assertNotIn('contraoferta',at.session_state)
            self.assertEqual(buscar.call_count,0)

    def test_area_cero_muestra_error_sin_resultados_anteriores(self):
        from unittest.mock import patch
        at=self.abrir()
        self.assertIn('contraoferta',at.session_state)
        with patch('motor_sprint4.reglas',[]):
            at.run()
        self.assertTrue(any('No se activó ninguna regla difusa.' in e.value for e in at.error))
        self.assertEqual(len(at.metric),0)
        self.assertNotIn('contraoferta',at.session_state)
        self.assertNotIn('evaluacion_actual',at.session_state)
        self.assertEqual(len(at.exception),0)
