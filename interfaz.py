"""Tema sin fuentes, imágenes ni scripts externos; adaptación al sistema operativo."""
import streamlit as st

OSCURO = '--surface:#0b1220;--panel:#111e30;--field:#15263b;--ink:#ecf3ff;--muted:#b6c6db;--line:#35465e;--accent:#53dcc5;--focus:#8bbaff;--action:#145e55;--action-ink:#ffffff;color-scheme:dark;'
CLARO = '--surface:#f5f7fb;--panel:#ffffff;--field:#edf2f8;--ink:#142338;--muted:#475b72;--line:#becbdc;--accent:#006858;--focus:#245ab2;--action:#006858;--action-ink:#ffffff;color-scheme:light;'


def aplicar_tema(tema):
    paleta = OSCURO if tema != 'Claro' else CLARO
    adaptativo = f'@media(prefers-color-scheme:light){{:root{{{CLARO}}}}}' if tema == 'Automático' else ''
    st.markdown('''<style>
:root{PALETA}
ADAPTATIVO
.stApp{--background-color:var(--surface);--secondary-background-color:var(--panel);--text-color:var(--ink);--primary-color:var(--accent);background:var(--surface);color:var(--ink)}
.block-container{max-width:1180px;padding-top:2.2rem;padding-bottom:3rem}
h1{letter-spacing:-.045em;line-height:1.15}h2,h3{letter-spacing:-.02em}
.stApp h1,.stApp h2,.stApp h3,.stApp p,.stApp label,.stApp [data-testid="stMetricValue"],.stApp [data-testid="stMetricLabel"]{color:var(--ink)}
.stApp [data-testid="stCaptionContainer"] p{color:var(--muted)}
[data-testid="stSidebar"]{background:var(--panel);border-right:1px solid var(--line)}
[data-testid="stMetric"]{background:var(--panel);padding:20px;border:1px solid var(--line);border-radius:14px;transition:border-color .15s ease,box-shadow .15s ease}
[data-testid="stMetric"]:hover{border-color:var(--accent);box-shadow:0 3px 12px #00000015}
[data-testid="stMetricValue"]{font-variant-numeric:tabular-nums}
.stApp [data-testid="stVerticalBlockBorderWrapper"]>div{border-color:var(--line)!important}
.stApp [data-baseweb="input"],.stApp [data-baseweb="base-input"],.stApp [data-baseweb="select"]>div{background:var(--field);color:var(--ink);border-color:var(--line)}
.stApp input{color:var(--ink)!important;-webkit-text-fill-color:var(--ink)}
.stApp button{transition:background-color .15s ease,border-color .15s ease;min-height:44px}
.stApp [data-testid="stNumberInput"] button,.stApp [data-testid="stBaseButton-secondary"],.stApp [data-testid="stBaseButton-downloadButton"]{background:var(--panel);color:var(--ink);border-color:var(--line)}
.stApp [data-testid="stBaseButton-primary"]{background:var(--action);border-color:var(--action);color:var(--action-ink)}
.stApp [data-testid="stBaseButton-primary"] p{color:var(--action-ink)}
.stApp a{color:var(--accent)}
.stApp :is(button,input,a,[role="switch"]):focus-visible{outline:3px solid var(--focus)!important;outline-offset:3px}
.stApp [data-testid="stAlert"]{border:1px solid var(--line);background:var(--panel)}
.stApp [data-testid="stTable"]{color:var(--ink);background:var(--panel)}
@media(max-width:640px){.block-container{padding:1.3rem 1rem}h1{font-size:2rem}[data-testid="stMetric"]{padding:14px}}
@media(prefers-reduced-motion:reduce){.stApp *{transition:none!important;animation:none!important;scroll-behavior:auto!important}}
</style>'''.replace('PALETA', paleta).replace('ADAPTATIVO', adaptativo), unsafe_allow_html=True)
