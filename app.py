import json
import random
import streamlit as st
from riesgo import evaluar_riesgo
from evolucion import estrategia_evolutiva, utilidad_cliente, utilidad_prestamista

st.set_page_config(page_title='Crédito · IA', page_icon='◈', layout='wide')
from interfaz import aplicar_tema

tema = st.sidebar.selectbox('Apariencia', ['Automático', 'Oscuro', 'Claro'], help='Automático sigue la preferencia de tu sistema.')
aplicar_tema(tema)

@st.cache_data(show_spinner=False, max_entries=64)
def buscar_contraoferta(cliente):
    # Conservar la semilla del Sprint 3 sin alterar el estado aleatorio del proceso.
    estado = random.getstate()
    try:
        random.seed(42)
        individuo, fitness, historial = estrategia_evolutiva(cliente)
    finally:
        random.setstate(estado)
    oferta = dict(cliente, monto_credito=individuo[0], plazo=individuo[1])
    return dict(individuo=individuo, fitness=fitness, historial=historial,
                evaluacion=evaluar_riesgo(oferta),
                utilidad_cliente=utilidad_cliente(*individuo, cliente),
                utilidad_prestamista=utilidad_prestamista(*individuo, cliente))

st.sidebar.title('◈ Crédito · IA')
st.sidebar.caption('FUNDAMENTOS DE INTELIGENCIA ARTIFICIAL')
pagina = st.sidebar.radio('Navegación', ['Evaluar solicitud', 'Cómo funciona', 'Proyecto y herramientas'])
st.sidebar.info('Prototipo académico. No constituye una decisión financiera real. No ingreses datos personales reales.')

if pagina == 'Evaluar solicitud':
    st.caption('SISTEMA INTELIGENTE DE CRÉDITO')
    st.title('Una solicitud. Una decisión explicada.')
    st.write('Evalúa el riesgo y explora una contraoferta cuando el perfil requiere revisión.')
    st.caption('ACTUALIZACIÓN EN VIVO · Confirma cada valor con Enter o al salir del campo.')
    with st.container(border=True):
        st.subheader('01 · Perfil financiero')
        a,b,c = st.columns(3, gap='large')
        with a:
            nombre = st.text_input('Alias del solicitante', 'Caso de ejemplo', max_chars=80)
            edad = st.number_input('Edad', 18, 100, 30)
            ingreso = st.number_input('Ingreso mensual (COP)', 1., 1e12, 4000000., step=100000.)
            score = st.number_input('Score crediticio', 0, 1000, 700, step=1, help='Escribe el valor exacto entre 0 y 1000.', key='score')
        with b:
            monto = st.number_input('Monto solicitado (COP)', 1., 1e12, 40000000., step=1000000.)
            meses = st.number_input('Plazo (meses)', 1, 240, 36)
            tasa = st.number_input('Tasa efectiva anual (%)', 0., 200., 18., step=.5)
        with c:
            deuda = st.number_input('Endeudamiento actual (%)', 0., 100., 40., step=.01, format='%.2f', help='Admite dos decimales, por ejemplo 42.75 %.', key='deuda')
            antiguedad = st.number_input('Antigüedad en empleo actual (años)', 0., 80., 4., step=.5)
            reportes = st.number_input('Reportes negativos', 0, 100, 0)
        st.caption('Endeudamiento: obligaciones actuales / ingreso. La cuota nueva se analiza por separado.')
    cliente = dict(nombre=nombre, edad=edad, ingreso_mensual=ingreso, monto_credito=monto, plazo=meses/12, tasa_anual=tasa, score=score, endeudamiento=deuda, antiguedad_empleo_actual=antiguedad, reportes_negativos=reportes)
    try:
        r = evaluar_riesgo(cliente)
    except ValueError as e:
        st.error(str(e))
        st.stop()
    # Una oferta anterior nunca se muestra para un perfil distinto.
    if st.session_state.get('perfil_oferta') != cliente:
        st.session_state.pop('contraoferta', None)
        st.session_state.pop('perfil_oferta', None)
    anterior = st.session_state.get('ultimo_riesgo')
    delta = None if anterior is None or abs(r['riesgo']-anterior) < 1e-9 else f"{r['riesgo']-anterior:+.2f} puntos"
    st.session_state['ultimo_riesgo'] = r['riesgo']
    st.subheader('02 · Evaluación en tiempo real')
    a,b,c = st.columns(3)
    a.metric('Decisión', r['decision'])
    b.metric('Riesgo global', f"{r['riesgo']:.2f} / 100", delta=delta, delta_color='inverse')
    c.metric('Cuota mensual', f"$ {r['cuota']:,.0f}")
    st.progress(r['riesgo']/100, text='Aprobado ≤35 · Revisión >35 y <65 · Rechazado ≥65')
    mensaje = {'APROBADO': st.success, 'REVISIÓN': st.warning, 'RECHAZADO': st.error}[r['decision']]
    mensaje(r['explicacion'])
    if st.toggle('Explorar trazabilidad difusa', key='trazabilidad'):
        with st.container(border=True):
            st.caption('Grados de pertenencia entre 0 y 1. Niveles de reglas: 0 bajo/malo, 1 medio, 2 alto/bueno.')
            st.table({k:dict(zip(['Bajo / malo','Medio','Alto / bueno'],v)) for k,v in r['membresias'].items()})
            st.dataframe([x for x in r['reglas'] if x['activacion']>0], width='stretch')
    if r['decision'] == 'REVISIÓN':
        st.subheader('03 · Explorar una alternativa')
        st.write('Busca un monto y plazo que reduzcan el riesgo, manteniendo el perfil y la tasa.')
        if st.button('Generar contraoferta', type='primary', width='stretch'):
            with st.spinner('Evaluando alternativas…'):
                st.session_state['contraoferta'] = buscar_contraoferta(cliente)
                st.session_state['perfil_oferta'] = cliente.copy()
        st.caption('μ=6 · λ=12 · 50 generaciones · La búsqueda se ejecuta solo al solicitarla.')
    resultado = {'cliente': cliente, 'evaluacion': r}
    if 'contraoferta' in st.session_state:
        o = st.session_state['contraoferta']
        resultado['contraoferta'] = o
        monto_oferta, plazo = o['individuo']
        if o['evaluacion']['decision'] != 'APROBADO':
            st.warning('La búsqueda no encontró una oferta aprobada. Esta alternativa no constituye una aprobación.')
        else:
            st.success('La alternativa cumple el umbral de aprobación del modelo académico.')
        a,b,c = st.columns(3)
        a.metric('Monto alternativo', f'$ {monto_oferta:,.0f}', delta=f"$ {monto_oferta-cliente['monto_credito']:,.0f}", delta_color='off')
        b.metric('Plazo alternativo', f'{round(plazo*12)} meses', delta=f"{round(plazo*12)-meses:+d} meses", delta_color='off')
        c.metric('Cuota alternativa', f"$ {o['evaluacion']['cuota']:,.0f}", delta=f"$ {o['evaluacion']['cuota']-r['cuota']:,.0f}", delta_color='inverse')
        st.write(o['evaluacion']['explicacion'])
        st.table({'Indicador':['Fitness','Utilidad cliente','Utilidad prestamista'], 'Valor':[o['fitness'],o['utilidad_cliente'],o['utilidad_prestamista']]})
        if st.toggle('Mostrar convergencia', key='convergencia'):
            st.line_chart({'Mejor fitness por generación': dict(enumerate(o['historial'],1))}, x_label='Generación', y_label='Fitness')
        st.caption('Semilla 42 · Las utilidades son índices heurísticos, no ganancias monetarias ni probabilidades.')
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
