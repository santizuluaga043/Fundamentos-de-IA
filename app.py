import json
import random
import streamlit as st
from riesgo import evaluar_riesgo
from evolucion import estrategia_evolutiva, utilidad_cliente, utilidad_prestamista

st.set_page_config(page_title='Crédito · IA', page_icon='◈', layout='wide')
st.markdown('''<style>.block-container{max-width:1120px;padding-top:2.5rem}h1{letter-spacing:-.045em}div[data-testid="stMetric"]{background:#f1f5f9;padding:18px;border-radius:12px;color:#0f172a}.stButton>button{border-radius:8px}</style>''', unsafe_allow_html=True)
st.sidebar.title('◈ Crédito · IA')
st.sidebar.caption('FUNDAMENTOS DE INTELIGENCIA ARTIFICIAL')
pagina = st.sidebar.radio('Navegación', ['Evaluar solicitud', 'Cómo funciona', 'Proyecto y herramientas'])
st.sidebar.info('Prototipo académico. No constituye una decisión financiera real. No ingreses datos personales reales.')

if pagina == 'Evaluar solicitud':
    st.caption('SISTEMA INTELIGENTE DE CRÉDITO')
    st.title('Una solicitud. Una decisión explicada.')
    st.write('Evalúa el riesgo y explora una contraoferta cuando el perfil requiere revisión.')
    with st.form('solicitud'):
        st.subheader('01 · Perfil financiero')
        a,b,c = st.columns(3)
        with a:
            nombre = st.text_input('Alias del solicitante', 'Caso de ejemplo', max_chars=80)
            edad = st.number_input('Edad', 18, 100, 30)
            ingreso = st.number_input('Ingreso mensual (COP)', 1., 1e12, 4000000., step=100000.)
            score = st.slider('Score crediticio', 0, 1000, 700)
        with b:
            monto = st.number_input('Monto solicitado (COP)', 1., 1e12, 40000000., step=1000000.)
            meses = st.number_input('Plazo (meses)', 1, 240, 36)
            tasa = st.number_input('Tasa efectiva anual (%)', 0., 200., 18., step=.5)
        with c:
            deuda = st.slider('Endeudamiento actual (%)', 0, 100, 40)
            antiguedad = st.number_input('Antigüedad en empleo actual (años)', 0., 80., 4., step=.5)
            reportes = st.number_input('Reportes negativos', 0, 100, 0)
        st.caption('Endeudamiento: obligaciones actuales / ingreso. La cuota nueva se analiza por separado; no se suma automáticamente a ese porcentaje.')
        enviar = st.form_submit_button('Evaluar solicitud', type='primary', use_container_width=True)
    if enviar:
        cliente = dict(nombre=nombre, edad=edad, ingreso_mensual=ingreso, monto_credito=monto, plazo=meses/12, tasa_anual=tasa, score=score, endeudamiento=deuda, antiguedad_empleo_actual=antiguedad, reportes_negativos=reportes)
        try:
            r = evaluar_riesgo(cliente)
            resultado = {'cliente': cliente, 'evaluacion': r}
            if r['decision'] == 'REVISIÓN':
                with st.spinner('Buscando una contraoferta durante 50 generaciones…'):
                    random.seed(42)
                    individuo, fitness, historial = estrategia_evolutiva(cliente)
                    oferta = dict(cliente, monto_credito=individuo[0], plazo=individuo[1])
                    resultado['contraoferta'] = dict(individuo=individuo, fitness=fitness, historial=historial, evaluacion=evaluar_riesgo(oferta), utilidad_cliente=utilidad_cliente(*individuo, cliente), utilidad_prestamista=utilidad_prestamista(*individuo, cliente))
            st.session_state['resultado'] = resultado
        except ValueError as e:
            st.session_state.pop('resultado', None)
            st.error(str(e))
    if 'resultado' in st.session_state:
        resultado = st.session_state['resultado']; r = resultado['evaluacion']
        st.subheader('02 · Resultado de la última evaluación')
        st.caption(f"Solicitante: {resultado['cliente']['nombre']}. Los cambios del formulario se aplican al volver a evaluar.")
        a,b,c = st.columns(3)
        a.metric('Decisión', r['decision']); b.metric('Riesgo global', f"{r['riesgo']:.2f} / 100"); c.metric('Cuota mensual', f"$ {r['cuota']:,.0f}")
        st.progress(r['riesgo']/100)
        st.write(r['explicacion'])
        with st.expander('Ver trazabilidad difusa'):
            st.write('Grados de pertenencia (0–1), de izquierda a derecha: bajo/malo, medio, alto/bueno.')
            st.table({k:dict(zip(['Bajo / malo','Medio','Alto / bueno'],v)) for k,v in r['membresias'].items()})
            st.dataframe([x for x in r['reglas'] if x['activacion']>0], use_container_width=True)
        if 'contraoferta' in resultado:
            o = resultado['contraoferta']; monto, plazo = o['individuo']
            st.subheader('03 · Alternativa encontrada')
            if o['evaluacion']['decision'] != 'APROBADO':
                st.warning('La búsqueda no encontró una oferta aprobada. Esta alternativa no debe presentarse como una aprobación.')
            else:
                st.success('La alternativa cumple el umbral de aprobación del modelo académico.')
            a,b,c = st.columns(3)
            a.metric('Monto alternativo', f'$ {monto:,.0f}'); b.metric('Plazo alternativo', f'{round(plazo*12)} meses'); c.metric('Cuota alternativa', f"$ {o['evaluacion']['cuota']:,.0f}")
            st.write(o['evaluacion']['explicacion'])
            st.table({'Indicador':['Fitness','Utilidad cliente','Utilidad prestamista'], 'Valor':[o['fitness'],o['utilidad_cliente'],o['utilidad_prestamista']]})
            st.line_chart({'Mejor fitness por generación': dict(enumerate(o['historial'],1))}, x_label='Generación', y_label='Fitness')
            st.caption('Semilla 42 · μ=6 · λ=12 · 50 generaciones. Las utilidades son índices heurísticos, no ganancias monetarias ni probabilidades.')
        st.download_button('Descargar evaluación JSON', json.dumps(resultado, ensure_ascii=False, indent=2), 'evaluacion.json', 'application/json')
elif pagina == 'Cómo funciona':
    st.title('Del sistema experto a la búsqueda evolutiva')
    st.subheader('Sprint 2 · Conocimiento del dominio')
    st.write('Aporta el perfil del solicitante, la estabilidad laboral por edad y el contrato de retorno (DECISIÓN, EXPLICACIÓN). Los notebooks originales se conservan en el repositorio.')
    st.subheader('Sistema de inferencia difuso · Riesgo continuo')
    st.write('FIS Sugeno de orden cero: score, endeudamiento y cuota/ingreso tienen tres conjuntos superpuestos. Las 27 combinaciones usan AND producto y defuzzificación por media ponderada de consecuentes constantes.')
    st.code('Score: 500, 650, 800\nDeuda (%): 30, 50, 70\nCuota/ingreso (%): 20, 30, 40\nConsecuente = 10 + 40 × [0.35 × (2-score_nivel) + 0.25 × deuda_nivel + 0.40 × cuota_nivel]')
    st.write('Los niveles son 0, 1 y 2. Los extremos usan hombros y el conjunto medio es triangular. El riesgo base va de 10 a 90. Estabilidad media añade 5 puntos y baja añade 10; un reporte añade 10. Dos o más reportes fijan un mínimo de 65. El resultado se limita a 100.')
    st.write('APROBADO: riesgo ≤35 · REVISIÓN: 35<riesgo<65 · RECHAZADO: riesgo ≥65. Se compara el valor sin redondear.')
    st.subheader('Sprint 3 · Contraofertas (μ+λ)')
    st.write('Solo se activa en REVISIÓN. Mantiene del 70 al 100 % del monto original y amplía el plazo hasta 240 meses, sin cambiar la tasa ni el perfil. Padres y descendientes compiten juntos; sobreviven los mejores seis.')
    st.code('Fitness = 0.50 × capacidad + 0.25 × cercanía_monto\n        + 0.25 × cercanía_plazo − penalización\nPenalización = 0 si la oferta es APROBADA; 1 en otro caso.')
    st.write('Se conservan las utilidades del notebook: cliente = 40 % monto + 30 % plazo + 30 % conveniencia de intereses; prestamista = 60 % capacidad + 40 % intereses relativos.')
    st.warning('Los pesos, pertenencias y umbrales no están calibrados con datos reales. El uso de edad y antigüedad heredado del notebook requiere revisión de equidad antes de cualquier aplicación real. La búsqueda es heurística y no garantiza un óptimo ni una oferta aprobada.')
else:
    st.title('Un proyecto, cuatro sprints')
    st.write('La aplicación integra el sistema experto del Sprint 2, la estrategia evolutiva del Sprint 3 y la propuesta de lógica difusa para el siguiente sprint. El Sprint 1 queda fuera del alcance, según la definición del proyecto.')
    st.subheader('Apoyo de inteligencia artificial')
    st.write('El autor utilizó ChatGPT y Gemini como apoyo para escribir código y estructurar el proyecto. En esta integración, ChatGPT/Codex apoyó la lectura de los notebooks, la implementación del FIS, la interfaz Streamlit, las pruebas y la preparación del despliegue. No se afirma que Gemini haya validado esta integración.')
    st.write('El análisis y la generación de contraofertas se ejecutan localmente con reglas y algoritmos; no se envían solicitudes a modelos generativos ni se requieren claves de API.')
    st.link_button('Consultar el repositorio', 'https://github.com/santizuluaga043/Fundamentos-de-IA')
