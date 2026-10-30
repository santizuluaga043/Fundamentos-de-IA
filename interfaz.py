"""Tema sin fuentes, imágenes ni scripts externos; adaptación al sistema operativo."""
import streamlit as st

OSCURO = '--surface:#0b1220;--panel:#102238;--field:#15263b;--ink:#ecf3ff;--muted:#b6c6db;--line:#35465e;--accent:#38D4C1;--focus:#8bbaff;--action:#145e55;--action-ink:#ffffff;color-scheme:dark;'
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
.stApp [data-testid="stAlert"]{border:0;background:transparent;box-shadow:none}
.stApp [data-testid="stTable"]{color:var(--ink);background:var(--panel)}
@media(max-width:640px){.block-container{padding:1.3rem 1rem}h1{font-size:2rem}[data-testid="stMetric"]{padding:14px}}
@media(prefers-reduced-motion:reduce){.stApp *{transition:none!important;animation:none!important;scroll-behavior:auto!important}}
</style>'''.replace('PALETA', paleta).replace('ADAPTATIVO', adaptativo), unsafe_allow_html=True)


def estilos_marca():
    st.markdown('''<style>
.cl-brand{display:flex;align-items:center;gap:16px}.cl-brand svg{width:64px;height:64px;flex-shrink:0}.cl-word{font-size:clamp(24px,4vw,38px);font-weight:750;letter-spacing:-1.2px;color:var(--ink)}.cl-word span{color:var(--accent)}.cl-word small{font-size:14px;letter-spacing:1px;color:var(--muted)}.cl-tag{font-size:13px;color:var(--muted)}
[data-testid="stSidebar"] .cl-brand{gap:10px}[data-testid="stSidebar"] .cl-brand svg{width:44px;height:44px}[data-testid="stSidebar"] .cl-word{font-size:23px}[data-testid="stSidebar"] .cl-tag{font-size:10px}
.cl-welcome{position:relative;border:1px solid var(--line);border-radius:20px;min-height:150px;padding:32px;background:var(--panel);overflow:hidden;margin-bottom:28px;display:flex;align-items:center}
.cl-finance{position:absolute;inset:12px 24px;display:flex;align-items:center;justify-content:center;gap:20px;color:var(--ink);animation:cl-away .3s 1.5s forwards}.cl-finance svg{width:min(45%,360px);height:90px}.cl-coin{display:grid;place-items:center;width:48px;height:48px;border:2px solid #38D4C1;border-radius:50%;font-size:28px;color:var(--accent);animation:cl-rise 1.3s both}.cl-finance-label{max-width:160px;font-size:14px}.cl-trend{stroke-dasharray:450;stroke-dashoffset:450;animation:cl-draw 1.4s ease forwards}.cl-intro .cl-final{animation:cl-reveal 2.1s both}
@keyframes cl-draw{to{stroke-dashoffset:0}}@keyframes cl-away{to{opacity:0;visibility:hidden;transform:translateY(-8px)}}@keyframes cl-rise{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}@keyframes cl-reveal{0%,78%{opacity:0;transform:translateY(8px)}100%{opacity:1;transform:translateY(0)}}
.cl-index{display:grid;gap:8px;margin:10px 0 26px}.cl-index a{display:flex;align-items:center;gap:12px;padding:12px 10px;border:1px solid var(--line);border-radius:12px;text-decoration:none!important;transition:border-color .15s,background .15s}.cl-index a:hover{border-color:var(--accent);background:var(--field)}.cl-index strong{display:block;font-size:14px;color:var(--ink)}.cl-index small{display:block;font-size:11px;color:var(--muted);margin-top:3px}.cl-step{background:#123A60;color:#38D4C1;border-radius:10px;min-width:32px;height:32px;display:grid;place-items:center;font-size:12px;font-weight:700}.cl-anchor{scroll-margin-top:90px}
.cl-risk{display:flex;gap:28px;align-items:center;background:var(--panel);border:1px solid var(--line);border-radius:18px;padding:24px;margin:16px 0}.cl-ring{width:132px;height:132px;flex-shrink:0;border-radius:50%;padding:9px;background:conic-gradient(var(--accent) var(--angle),var(--line) 0deg)}.cl-ring>div{background:var(--panel);height:100%;border-radius:50%;display:flex;flex-direction:column;justify-content:center;align-items:center}.cl-ring strong{font-size:30px;color:var(--ink);font-variant-numeric:tabular-nums}.cl-ring small{font-size:11px;color:var(--muted)}.cl-eyebrow{font-size:10px;letter-spacing:1.5px;color:var(--accent)}.cl-risk h3{margin:5px 0}.cl-risk p{font-size:14px;color:var(--muted);margin:0}
@media(max-width:640px){.cl-welcome{padding:20px}.cl-risk{gap:15px;padding:16px}.cl-ring{width:95px;height:95px}.cl-ring strong{font-size:23px}.cl-risk h3{font-size:18px}.cl-finance-label{display:none}}
@media(prefers-reduced-motion:reduce){.cl-finance{display:none!important}.cl-final{opacity:1!important;transform:none!important;animation:none!important}}
</style>''', unsafe_allow_html=True)
