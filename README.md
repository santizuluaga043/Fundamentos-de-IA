# Credi Logic AI

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

## Interfaz adaptativa y rendimiento

La apariencia se selecciona en la barra lateral: Automático sigue `prefers-color-scheme` del sistema, Oscuro y Claro fijan la paleta. Los colores de superficies, textos y controles se adaptan juntos. Se usa Nunito local con respaldo de fuentes del sistema, foco visible, controles de al menos 44 px, cifras tabulares y transiciones cortas desactivadas con `prefers-reduced-motion`. Las decisiones incluyen texto e iconos y no dependen solo del color.

Los campos se confirman con Enter o al perder el foco. Score admite enteros y endeudamiento dos decimales; ya no hay sliders. El FIS se recalcula al confirmar cada ajuste. La generación evolutiva se solicita con **Generar contraoferta** y se almacena en caché para hasta 64 perfiles. Si cambia cualquier dato, desaparece la oferta anterior. La trazabilidad y la gráfica se construyen solo cuando se activan sus controles; no hay fuentes, imágenes ni scripts remotos añadidos por la interfaz.

Medición local con Streamlit AppTest (Python 3.12): primera ejecución incluyendo imports 0.393 s; mediana de cinco cambios de score 0.016 s (máximo 0.016 s); búsqueda evolutiva más render 0.293 s. Salud HTTP: `ok`. Estos tiempos miden ejecución local, no carga visual en un navegador ni latencia de Community Cloud. El objetivo de carga inferior a 2.5 s debe verificarse en el despliegue público; los arranques tras reposo y la red pueden superarlo. La inspección visual posterior se realizó con Chromium disponible en el sistema; se verificaron escritorio, móvil y movimiento reducido.


## Identidad y recorrido guiado

Credi Logic AI utiliza un símbolo C con nodos, azul marino `#123A60`, turquesa `#38D4C1` y blanco. Los recursos vectoriales están en `assets/` y la presentación se implementa en `marca.py`. La bienvenida dibuja una tendencia financiera y revela el logo en 2.1 segundos, una sola vez por sesión, sin bloquear el formulario ni ejecutar esperas. Con movimiento reducido el logo aparece directamente.

El índice lateral enlaza a cinco secciones: Tu solicitud, Tu resultado, Entiende la decisión, Busca una alternativa y Compara las opciones. Todos los destinos existen incluso sin contraoferta y explican cuándo está disponible cada paso. El perfil y la alternativa se conservan al navegar a Cómo funciona y regresar. Los detalles de reglas, fitness, utilidades numéricas y convergencia están en Cómo funciona. La comparación principal muestra montos, plazos, cuotas e intereses totales; una extensión del plazo incluye una advertencia visible sobre el costo.

Validación de esta versión: ocho pruebas del modelo y cinco de interfaz; comprobación en Chromium de los enlaces del índice, generación de alternativa, logo final, móvil sin desbordamiento horizontal y preferencia de movimiento reducido. Tiempo local de navegador hasta mostrar la interfaz e índice: 1.876 s; no es una medición de Community Cloud ni una garantía de carga pública. La portada de GitHub Pages también utiliza la nueva identidad.

El plazo de entrada se expresa en años (por ejemplo 3.5 años = 42 meses). El motor recibe años y convierte internamente a meses para la amortización; se rechazan plazos que no equivalgan a meses completos. Las contraofertas y la comparación mantienen la duración en meses para mostrar su valor exacto.


La navegación general se encuentra debajo del recorrido, en la parte inferior de la barra lateral. La barra abierta mide 292 px y utiliza los controles nativos de Streamlit para ocultarse y expandirse; el control de cierre permanece visible y el de reapertura indica «Menú». En móvil comienza plegada y mantiene un ancho limitado al espacio disponible.

Tipografía: Nunito variable, distribuida localmente como WOFF2 (48,912 bytes) para textos, títulos y controles, sin solicitudes a Google Fonts. Fuente original: https://github.com/google/fonts/tree/main/ofl/nunito ; subconjunto latino con caracteres españoles. Se conservan la atribución y licencia SIL OFL 1.1 en `assets/Nunito-OFL.txt` y `docs/Nunito-OFL.txt`. Los iconos nativos mantienen su tipografía de símbolos. La misma fuente se aplica a la portada de Pages.
