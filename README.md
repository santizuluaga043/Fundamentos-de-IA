# Credi Logic AI

Aplicación académica Streamlit que integra los notebooks originales de los sprints 2, 3 y 4 y el FIS Mamdani del Sprint 4. El Sprint 1 no forma parte de la aplicación.

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

`riesgo.motor_inferencia(cliente)` mantiene el retorno `(DECISIÓN, EXPLICACIÓN)`. `motor_sprint4.py` conserva las funciones, pertenencias, 27 reglas explícitas e inferencia del notebook Sprint-4, sin ejecutar su entrada interactiva ni sus gráficos. El FIS es Mamdani: AND mínimo, recorte de salida, agregación máximo y centroide con `np.trapezoid` sobre 1001 puntos entre 0 y 100. NumPy 2 o superior es necesario.

La decisión financiera es APROBADO si índice ≤35, RECHAZADO si índice ≥65 y REVISIÓN entre ambos. El sistema experto conserva las restricciones: dos o más reportes fuerzan rechazo; un reporte o estabilidad MEDIA/BAJA pueden convertir aprobación en revisión y exigen validación personal. Estas condiciones no suman puntos al índice. El adaptador separa `decision_financiera`, `revision_manual`, `motivos_revision` y `ejecutar_evolutiva` de la decisión final.

La estrategia se ejecuta automáticamente solo en revisión por capacidad de pago: **35 < índice difuso < 65**, sin revisión personal, sin reportes negativos y con una comprobación de que el mismo score y endeudamiento permitirían aprobar si la cuota fuera baja (≤15 % del ingreso). Esta comprobación es diagnóstica; no constituye una oferta ni garantiza una solución dentro de los límites de búsqueda. Si aun con una cuota baja el índice supera 35, no se habilita la búsqueda. El botón permanece desactivado y se explica el motivo. La caché y el estado evitan repetir la búsqueda para el mismo perfil. Esta condición sustituye la habilitación anterior que también permitía buscar con revisión personal pendiente. Las decisiones del notebook y el fitness financiero se mantienen.


`evolucion.py` conserva la búsqueda, cuotas, utilidades, mutación, reparación y selección del notebook; la única excepción deliberada es el fitness solicitado: la penalización es cero si el riesgo difuso de la oferta ≤35 y uno en caso contrario, independientemente de la revisión personal. Semilla 42, μ=6, λ=12 y 50 generaciones; monto 70–100 % del original y plazo original–240 meses completos. Una oferta financieramente viable con revisión personal pendiente se anuncia como sujeta a validación de un funcionario. No se garantiza óptimo ni factibilidad.

**Comportamiento heredado que se conserva:** `np.interp` con extremos repetidos produce pertenencia cero en algunos límites, como score 1000 y endeudamiento 100 %. Las cuotas/ingresos superiores al universo también pueden dejar todas las reglas inactivas. En esos casos el notebook devuelve **50**, y esta integración hace lo mismo para respetar la equivalencia. No se corrigieron silenciosamente estos casos ni los límites de plazo del algoritmo.

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

Los campos se confirman con Enter o al perder el foco. Score admite enteros y endeudamiento dos decimales; ya no hay sliders. El FIS se recalcula al confirmar cada ajuste. La generación evolutiva se activa por el intervalo de riesgo financiero y se almacena en caché para hasta 64 perfiles. Si cambia cualquier dato, se descarta la oferta anterior y se genera otra solo si corresponde. La trazabilidad y la gráfica se muestran en Cómo funciona; no hay fuentes, imágenes ni scripts remotos añadidos por la interfaz.

Medición histórica del motor anterior con Streamlit AppTest (Python 3.12): primera ejecución incluyendo imports 0.393 s; mediana de cinco cambios de score 0.016 s (máximo 0.016 s); búsqueda evolutiva más render 0.293 s. Salud HTTP: `ok`. Estos tiempos miden ejecución local, no carga visual en un navegador ni latencia de Community Cloud. El objetivo de carga inferior a 2.5 s debe verificarse en el despliegue público; los arranques tras reposo y la red pueden superarlo. La inspección visual posterior se realizó con Chromium disponible en el sistema; se verificaron escritorio, móvil y movimiento reducido.


## Identidad y recorrido guiado

Credi Logic AI utiliza un símbolo C con nodos, azul marino `#123A60`, turquesa `#38D4C1` y blanco. Los recursos vectoriales están en `assets/` y la presentación se implementa en `marca.py`. La bienvenida dibuja una tendencia financiera y revela el logo en 2.1 segundos, una sola vez por sesión, sin bloquear el formulario ni ejecutar esperas. Con movimiento reducido el logo aparece directamente.

El índice lateral enlaza a cinco secciones: Tu solicitud, Tu resultado, Entiende la decisión, Busca una alternativa y Compara las opciones. Todos los destinos existen incluso sin contraoferta y explican cuándo está disponible cada paso. El perfil y la alternativa se conservan al navegar a Cómo funciona y regresar. Los detalles de reglas, fitness, utilidades numéricas y convergencia están en Cómo funciona. La comparación principal muestra montos, plazos, cuotas e intereses totales; una extensión del plazo incluye una advertencia visible sobre el costo.

Validación histórica del rediseño: ocho pruebas del modelo y cinco de interfaz; comprobación en Chromium de los enlaces del índice, generación de alternativa, logo final, móvil sin desbordamiento horizontal y preferencia de movimiento reducido. Tiempo local de navegador hasta mostrar la interfaz e índice: 1.876 s; no es una medición de Community Cloud ni una garantía de carga pública. La portada de GitHub Pages también utiliza la nueva identidad.

El plazo de entrada se expresa en años (por ejemplo 3.5 años = 42 meses). El motor recibe años y convierte internamente a meses para la amortización; se rechazan plazos que no equivalgan a meses completos. Las contraofertas y la comparación mantienen la duración en meses para mostrar su valor exacto.


La navegación general se encuentra debajo del recorrido, en la parte inferior de la barra lateral. La barra abierta mide 292 px y utiliza los controles nativos de Streamlit para ocultarse y expandirse; el control de cierre permanece visible y el de reapertura indica «Menú». En móvil comienza plegada y mantiene un ancho limitado al espacio disponible.

Tipografía: Nunito variable, distribuida localmente como WOFF2 (48,912 bytes) para textos, títulos y controles, sin solicitudes a Google Fonts. Fuente original: https://github.com/google/fonts/tree/main/ofl/nunito ; subconjunto latino con caracteres españoles. Se conservan la atribución y licencia SIL OFL 1.1 en `assets/Nunito-OFL.txt` y `docs/Nunito-OFL.txt`. Los iconos nativos mantienen su tipografía de símbolos. La misma fuente se aplica a la portada de Pages.


## Integración del Sprint 4

Rama `feat/sprint4-motor`, basada en `a0e3e29`. El diseño, los recursos, el logo, la fuente y la navegación permanecen sin cambios. Solo se adaptan el motor, sus conexiones, los mensajes de revisión personal y las explicaciones técnicas autorizadas. El despliegue actual en `main` no se modifica al publicar esta rama.

Validación: 14 pruebas del modelo y 13 de interfaz, incluyendo 104 perfiles comparados directamente con una carga independiente de funciones del notebook; reglas idénticas; búsqueda y fitness iguales al notebook con la excepción financiera solicitada; revisión exclusivamente personal, revisión combinada, rechazo prioritario, límites 35/65, respaldo de 50, cachés de versiones previas, una ejecución por perfil y un solo gráfico. El notebook se guarda íntegro en `notebooks/Sprint-4.ipynb`.
