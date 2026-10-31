"""Identidad y animación locales: SVG/CSS, sin red ni espera artificial."""
import streamlit as st

SIMBOLO = '''<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><rect width="100" height="100" rx="22" fill="#123A60"/><path d="M65 28 A28 28 0 1 0 65 72" fill="none" stroke="white" stroke-width="9" stroke-linecap="round"/><path d="M65 28 L72 50 L65 72" fill="none" stroke="#38D4C1" stroke-width="3"/><g fill="#38D4C1"><circle cx="65" cy="28" r="5.5"/><circle cx="72" cy="50" r="5.5"/><circle cx="65" cy="72" r="5.5"/></g></svg>'''


DIBUJOS = {
    'perfil': '<rect x="6" y="3" width="20" height="26" rx="4"/><circle cx="16" cy="12" r="4"/><path d="M10 24q6-8 12 0"/>',
    'resultado': '<path d="M16 3L28 8v8c0 7-12 13-12 13S4 23 4 16V8Z"/><path d="m10 16 4 4 8-9"/>',
    'explicacion': '<circle cx="14" cy="14" r="10"/><path d="m22 22 7 7M14 8v7m0 4v1"/>',
    'comparacion': '<path d="M4 27h24M8 24V14h5v10m6 0V5h5v19"/>',
}

def logo():
    return '<div class="cl-brand">'+SIMBOLO+'<div><div class="cl-word">Credi<span>Logic</span> <small>AI</small></div><div class="cl-tag">Inteligencia aplicada al crédito</div></div></div>'


def bienvenida():
    primera = not st.session_state.get('bienvenida_vista', False)
    st.session_state['bienvenida_vista'] = True
    animacion = '''<div class="cl-finance" aria-hidden="true"><span class="cl-coin">$</span><svg viewBox="0 0 400 100"><path d="M5 90H395" stroke="#54718c" fill="none"/><path class="cl-trend" d="M10 80 L80 65 L140 72 L210 35 L280 45 L380 10" stroke="#38D4C1" stroke-width="5" fill="none"/><circle cx="380" cy="10" r="6" fill="#38D4C1"/></svg><span class="cl-finance-label">Tu perfil → Una decisión clara</span></div>'''
    st.markdown('<div class="cl-welcome '+('cl-intro' if primera else '')+'">'+(animacion if primera else '')+'<div class="cl-final">'+logo()+'</div></div>', unsafe_allow_html=True)


def indice(decision, tiene_oferta, contenedor=None):
    pasos = [('perfil','01','Tu solicitud','Ingresa tus datos'),
             ('resultado','02','Tu resultado',decision.capitalize()),
             ('explicacion','03','Entiende la decisión','Qué se tuvo en cuenta'),
             ('comparacion','04','Compara las opciones','Alternativa lista' if tiene_oferta else 'Después de la búsqueda')]
    enlaces = ''.join(f'<a href="#{destino}" target="_self" aria-label="{titulo}" title="{titulo}"><svg viewBox="0 0 32 32" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8">{DIBUJOS[destino]}</svg><span class="cl-tip">{titulo}</span></a>' for destino,n,titulo,sub in pasos)
    (contenedor or st.sidebar).markdown('<div class="cl-eyebrow">TU RECORRIDO</div><nav class="cl-index" aria-label="Paso a paso de tu evaluación">'+enlaces+'</nav>', unsafe_allow_html=True)


def ancla(nombre):
    st.markdown(f'<div id="{nombre}" class="cl-anchor"></div>', unsafe_allow_html=True)


def panorama(riesgo):
    st.markdown(f'''<div class="cl-risk" role="img" aria-label="Índice de riesgo {riesgo:.2f} de 100"><div class="cl-ring" style="--angle:{riesgo*3.6:.3f}deg"><div><strong>{riesgo:.1f}</strong><small>de 100 · riesgo</small></div></div><div><span class="cl-eyebrow">UNA LECTURA DE TU PERFIL</span><h3>Más claridad para decidir</h3><p>Un valor menor indica un perfil más favorable según este modelo. No representa una probabilidad de impago.</p></div></div>''', unsafe_allow_html=True)
