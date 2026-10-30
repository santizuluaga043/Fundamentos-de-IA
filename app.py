import json
import random
import streamlit as st
from riesgo import evaluar_riesgo
from evolucion import estrategia_evolutiva, utilidad_cliente, utilidad_prestamista

st.set_page_config(page_title='Credi Logic AI · Tu crédito, con claridad', page_icon='assets/favicon.png', layout='wide', initial_sidebar_state='auto')
import interfaz

# Los estilos no guardan estado: recargarlos evita conservar CSS anterior
# cuando Community Cloud sincroniza nuevos archivos sin reiniciar el proceso.
import importlib
importlib.invalidate_caches()
importlib.reload(interfaz)

from interfaz import aplicar_tema, estilos_marca
from marca import logo, bienvenida, indice, ancla, panorama

# Migrar el plazo de las sesiones que usaban el campo en meses.
if 'plazo_anios' not in st.session_state and 'meses' in st.session_state:
    st.session_state['plazo_anios'] = st.session_state['meses'] / 12

# Conservar el perfil al abrir las páginas de explicación.
for campo in ('alias', 'edad', 'ingreso', 'score', 'monto', 'plazo_anios', 'tasa', 'deuda', 'antiguedad', 'reportes'):
    if campo in st.session_state:
        st.session_state[campo] = st.session_state[campo]

st.sidebar.markdown(logo(), unsafe_allow_html=True)
tema = st.sidebar.selectbox('Apariencia', ['Automático', 'Oscuro', 'Claro'], help='Automático sigue la preferencia de tu sistema.')
aplicar_tema(tema)
estilos_marca()

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

st.sidebar.caption('FUNDAMENTOS DE INTELIGENCIA ARTIFICIAL')
guia = st.sidebar.container()
with st.sidebar.container(key='sidebar_footer'):
    st.divider()
    pagina = st.radio('Navegación', ['Evaluar solicitud', 'Cómo funciona', 'Proyecto y herramientas'])
    st.caption('Prototipo académico. No constituye una decisión financiera real. No ingreses datos personales reales.')

if pagina == 'Evaluar solicitud':
    bienvenida()
    st.title('Tu crédito, con claridad.')
    st.write('Conoce tu resultado, entiende los motivos y descubre si hay una alternativa para ti.')
    ancla('perfil')
    st.caption('ACTUALIZACIÓN EN VIVO · Confirma cada valor con Enter o al salir del campo.')
    with st.container(border=True):
        st.subheader('01 · Cuéntanos qué necesitas')
        a,b,c = st.columns(3, gap='large')
        with a:
            nombre = st.text_input('Nombre', 'Caso de ejemplo', max_chars=80, key='alias')
            edad = st.number_input('Edad', 18, 100, 30, key='edad')
            ingreso = st.number_input('Ingreso mensual (COP)', 1., 1e12, 4000000., step=100000., key='ingreso')
            score = st.number_input('Score crediticio', 0, 1000, 700, step=1, help='Escribe el valor exacto entre 0 y 1000.', key='score')
        with b:
            monto = st.number_input('Monto solicitado (COP)', 1., 1e12, 40000000., step=1000000., key='monto')
            plazo_anios = st.number_input('Plazo (años)', 0., 20., 3., step=.5, format='%.2f', key='plazo_anios', help='Mayor que 0 y hasta 20 años. Admite fracciones equivalentes a meses completos, por ejemplo 3.5 años = 42 meses.')
            meses = round(plazo_anios * 12)
            st.caption(f'{plazo_anios:g} años × 12 = {plazo_anios * 12:g} meses. El cálculo usa meses completos.')
            tasa = st.number_input('Tasa efectiva anual (%)', 0., 200., 18., step=.5, key='tasa')
        with c:
            deuda = st.number_input('Endeudamiento actual (%)', 0., 100., 40., step=.01, format='%.2f', help='Admite dos decimales, por ejemplo 42.75 %.', key='deuda')
            antiguedad = st.number_input('Antigüedad en empleo actual (años)', 0., 80., 4., step=.5, key='antiguedad')
            reportes = st.number_input('Reportes negativos', 0, 100, 0, key='reportes')
        st.caption('Endeudamiento: obligaciones actuales / ingreso. La cuota nueva se analiza por separado.')
    cliente = dict(nombre=nombre, edad=edad, ingreso_mensual=ingreso, monto_credito=monto, plazo=plazo_anios, tasa_anual=tasa, score=score, endeudamiento=deuda, antiguedad_empleo_actual=antiguedad, reportes_negativos=reportes)
    try:
        r = evaluar_riesgo(cliente)
    except ValueError as e:
        st.error(str(e))
        st.stop()
    st.session_state['evaluacion_actual'] = r
    # Una oferta anterior nunca se muestra para un perfil distinto.
    if st.session_state.get('perfil_oferta') != cliente:
        st.session_state.pop('contraoferta', None)
        st.session_state.pop('perfil_oferta', None)
    anterior = st.session_state.get('ultimo_riesgo')
    delta = None if anterior is None or abs(r['riesgo']-anterior) < 1e-9 else f"{r['riesgo']-anterior:+.2f} puntos"
    st.session_state['ultimo_riesgo'] = r['riesgo']
    with guia:
        indice(r['decision'], 'contraoferta' in st.session_state, contenedor=guia)
    ancla('resultado')
    st.subheader('02 · Este es tu resultado')
    panorama(r['riesgo'])
    a,b,c = st.columns(3)
    a.metric('Decisión', r['decision'])
    b.metric('Riesgo global', f"{r['riesgo']:.2f} / 100", delta=delta, delta_color='inverse')
    c.metric('Cuota mensual', f"$ {r['cuota']:,.0f}")
    st.progress(r['riesgo']/100, text='Aprobado ≤35 · Revisión >35 y <65 · Rechazado ≥65')
    mensaje = {'APROBADO': st.success, 'REVISIÓN': st.warning, 'RECHAZADO': st.error}[r['decision']]
    textos = {
        'APROBADO': 'Tu solicitud cumple el umbral de aprobación de esta simulación.',
        'REVISIÓN': 'Tu solicitud necesita una segunda mirada. Podemos explorar otro monto o plazo.',
        'RECHAZADO': 'Tu solicitud no cumple el umbral de esta simulación. Revisa los factores de tu perfil antes de volver a evaluar.',
    }
    mensaje(textos[r['decision']])
    ancla('explicacion')
    st.subheader('03 · ¿Qué se tuvo en cuenta?')
    st.write('Miramos tu historial, tus obligaciones actuales y cuánto representa la nueva cuota en tus ingresos. La estabilidad laboral y los reportes también pueden aumentar el riesgo.')
    columnas = st.columns(3)
    etiquetas = [
        ('Tu historial', ['Por fortalecer', 'Intermedio', 'Favorable'], f"Score informado: {score}. Un valor mayor mejora este factor."),
        ('Tus obligaciones', ['Carga baja', 'Carga intermedia', 'Carga alta'], f"Ya destinas {deuda:.2f} % de tus ingresos a obligaciones actuales."),
        ('La nueva cuota', ['Carga baja', 'Carga intermedia', 'Carga alta'], f"La cuota nueva representa el {r['relacion']:.1f} % de tus ingresos mensuales."),
    ]
    for col, (titulo, niveles, detalle), grados in zip(columnas, etiquetas, r['membresias'].values()):
        nivel = max(range(3), key=lambda i: grados[i])
        with col:
            with st.container(border=True):
                st.markdown(f'**{titulo} · {niveles[nivel]}**')
                st.write(detalle)
    st.caption('Estas etiquetas resumen cada factor. El resultado combina todos los valores de forma gradual; ninguna etiqueta explica por sí sola la decisión.')
    if cliente['reportes_negativos'] >= 2:
        st.warning('Hay dos o más reportes negativos: el modelo mantiene el resultado en rechazo aunque otros factores sean favorables.')
    elif cliente['reportes_negativos'] == 1:
        st.info('Un reporte negativo aumenta el riesgo de esta solicitud.')
    if r['estabilidad'] in ('MEDIA', 'BAJA'):
        st.info('La antigüedad laboral informada añade cautela a la evaluación según los criterios del proyecto.')
    ancla('alternativa')
    st.subheader('04 · ¿Podemos encontrar otra opción?')
    if r['decision'] == 'REVISIÓN':
        st.write('Busca un monto y plazo que reduzcan el riesgo, manteniendo el perfil y la tasa.')
        if st.button('Generar contraoferta', type='primary', width='stretch'):
            with st.spinner('Evaluando alternativas…'):
                st.session_state['contraoferta'] = buscar_contraoferta(cliente)
                st.session_state['perfil_oferta'] = cliente.copy()
        st.caption('Comparamos distintas combinaciones para buscar una cuota más manejable y conservar, en lo posible, el monto y el plazo que necesitas.')
    else:
        st.info('La búsqueda de alternativas se activa cuando tu resultado es REVISIÓN. Con aprobación ya cumples el umbral; con rechazo es necesario revisar el perfil primero.')
    ancla('comparacion')
    st.subheader('05 · Compara antes de decidir')
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
        st.write(f"El riesgo de la alternativa es {o['evaluacion']['riesgo']:.2f}/100. Su nueva cuota representa el {o['evaluacion']['relacion']:.1f} % de tus ingresos.")
        interes_original = r['cuota'] * meses - cliente['monto_credito']
        interes_oferta = o['evaluacion']['cuota'] * round(plazo*12) - monto_oferta
        st.table({'Concepto': ['Monto (COP)', 'Plazo (meses)', 'Cuota mensual (COP)', 'Intereses totales estimados (COP)'],
                  'Tu solicitud': [f"{cliente['monto_credito']:,.0f}", str(meses), f"{r['cuota']:,.0f}", f"{interes_original:,.0f}"],
                  'Alternativa': [f'{monto_oferta:,.0f}', str(round(plazo*12)), f"{o['evaluacion']['cuota']:,.0f}", f'{interes_oferta:,.0f}']})
        if plazo*12 > meses:
            st.warning('Una cuota más baja puede implicar pagar durante más tiempo y mayores intereses. Compara el costo total, no solo la cuota mensual.')
        st.markdown('**¿Por qué se eligió esta alternativa?**')
        st.write('La búsqueda valora una cuota manejable, conservar el monto solicitado y evitar alargar demasiado el plazo. Las opciones que no alcanzan la aprobación reciben una penalización.')
        izquierda, derecha = st.columns(2)
        with izquierda:
            st.write('**Ajuste a tus preferencias**')
            st.progress(max(0., min(1., o['utilidad_cliente'])))
            st.caption('Resume cuánto conserva la opción de tu monto, plazo y conveniencia de intereses.')
        with derecha:
            st.write('**Equilibrio para quien presta**')
            st.progress(max(0., min(1., o['utilidad_prestamista'])))
            st.caption('Combina la capacidad de pagar la cuota y los intereses previstos.')
        st.caption('Son comparaciones del modelo, no probabilidades, ganancias garantizadas ni una oferta de crédito real. Consulta Cómo funciona para ver los cálculos.')
    else:
        st.info('Aquí verás el monto, el plazo, la cuota y el costo de intereses de ambas opciones cuando generes una alternativa.')
    st.download_button('Descargar evaluación JSON', json.dumps(resultado, ensure_ascii=False, indent=2), 'evaluacion.json', 'application/json')

elif pagina == 'Cómo funciona':
    st.title('Cómo funciona Credi Logic AI')
    st.caption('DETALLE TÉCNICO · Motor de riesgo y búsqueda de alternativas')
    if 'contraoferta' in st.session_state:
        o = st.session_state['contraoferta']
        st.subheader('Cálculos de la última alternativa')
        st.table({'Indicador': ['Fitness', 'Utilidad cliente', 'Utilidad prestamista'], 'Valor': [o['fitness'], o['utilidad_cliente'], o['utilidad_prestamista']]})
        st.line_chart({'Mejor fitness por generación': dict(enumerate(o['historial'], 1))}, x_label='Generación', y_label='Fitness')
        st.caption('Semilla 42 · μ=6 · λ=12 · 50 generaciones. El fitness puede ser negativo si la alternativa no cumple la aprobación.')
    else:
        st.info('Genera una alternativa en Evaluar solicitud para consultar aquí su fitness, utilidades y evolución.')
    if 'evaluacion_actual' in st.session_state:
        r = st.session_state['evaluacion_actual']
        with st.expander('Trazabilidad del perfil actual'):
            st.write(r['explicacion'])
            st.table({k: dict(zip(['Bajo / malo', 'Medio', 'Alto / bueno'], v)) for k, v in r['membresias'].items()})
            st.dataframe([x for x in r['reglas'] if x['activacion'] > 0], width='stretch')
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
