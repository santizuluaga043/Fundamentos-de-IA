# Crédito · IA

Aplicación académica Streamlit que integra los notebooks originales de los sprints 2 y 3 y un nuevo FIS Sugeno. El Sprint 1 no forma parte de la aplicación.

## Ejecución

Python 3.12:

```sh
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m unittest discover -s tests_ui -v
```

## Modelo

`riesgo.motor_inferencia(cliente)` mantiene el retorno `(DECISIÓN, EXPLICACIÓN)`. La decisión usa el riesgo sin redondear: APROBADO ≤35, RECHAZADO ≥65, REVISIÓN entre ambos. El FIS sustituye las clasificaciones rígidas de score, deuda y capacidad. Las 27 reglas Sugeno usan AND producto, consecuentes constantes y media ponderada. Los puntos de pertenencia son score 500/650/800, deuda 30/50/70 %, cuota/ingreso 20/30/40 %. Los niveles 0/1/2 producen `10+40*(.35*(2-score)+.25*deuda+.40*cuota)`. Estabilidad media añade 5 y baja 10, un reporte añade 10, dos o más imponen riesgo mínimo 65. Se limita a 100. No es una probabilidad calibrada.

`evolucion.py` conserva las funciones de cuotas, estabilidad, fitness, utilidades, mutación, reparación y selección del Sprint 3. La interfaz usa semilla 42, μ=6, λ=12 y 50 generaciones. Solo se ejecuta para REVISIÓN. El monto queda entre 70 y 100 % del original, el plazo entre el original y 240 meses completos. Las ofertas se reevalúan con el FIS; una alternativa no aprobada se indica expresamente. La búsqueda no garantiza óptimo ni factibilidad. El endeudamiento actual y la cuota nueva son entradas separadas, tal como en el notebook.

Los notebooks se preservan en `notebooks/`. Sus programas interactivos no se ejecutan al importar la aplicación.

## Publicación

1. Publicar este contenido en la rama `main` de `santizuluaga043/Fundamentos-de-IA`.
2. GitHub: Settings → Pages → Source: GitHub Actions. El workflow valida el modelo y la interfaz antes de publicar `docs/`.
3. Streamlit Community Cloud: conectar GitHub, seleccionar este repositorio, rama `main`, archivo `app.py` y Python 3.12. No se necesitan secretos ni APIs de IA.
4. Tras obtener la URL real de Streamlit, añadirla a `docs/index.html`. No se presupone un subdominio disponible.

GitHub Pages sirve la portada estática; no ejecuta Python. El despliegue de Streamlit requiere acceso a una cuenta de Community Cloud.

## Uso de IA y límites

El autor declara apoyo de ChatGPT y Gemini para código y estructura. ChatGPT/Codex apoyó esta integración, el FIS, la interfaz y las pruebas. No se atribuye a Gemini validación de esta versión. El programa no llama modelos generativos.

Prototipo educativo sin calibración con datos, auditoría de equidad ni validación para crédito real. Edad y antigüedad conservan criterios del notebook que deben revisarse antes de cualquier uso real. No introducir datos personales reales. La sesión mantiene la evaluación en memoria y permite descargarla; no se utiliza base de datos.
