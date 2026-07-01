import streamlit as st
import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader
import io
import re
from deep_translator import GoogleTranslator

# Configuración de interfaz premium responsiva
st.set_page_config(page_title="Nexus Mobile Pure", page_icon="📖", layout="wide")

# --- CONTROL DE SESIÓN NATIVO (ESTADOS DE PYTHON) ---
if "datos_lectura" not in st.session_state:
    st.session_state.datos_lectura = None
if "historial_urls" not in st.session_state:
    st.session_state.historial_urls = []

# --- MOTOR DE SEGURIDAD Y LIMPIEZA DE ENLACES ---
def desinfectar_texto(texto):
    if not texto: return ""
    patron_url = r'(https?://[^\s<>"]+|www\.[^\s<>"]+|\b[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}\b(/[^\s<>"]*)?)'
    return re.sub(patron_url, "[⚠️ Enlace Bloqueado]", texto).strip()

# --- MOTORES DE EXTRACCIÓN CON OPTIMIZACIÓN DE MEMORIA CACHÉ ---
@st.cache_data(show_spinner=False)
def extraer_web_optimizada(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        titulo = soup.find('h1').text.strip() if soup.find('h1') else "Capítulo Online"
        
        for b in soup(["script", "style", "iframe", "object", "embed", "form", "button", "nav", "footer"]): 
            b.decompose()
            
        contenedor = soup.select_one('div[class*="chapter"], div[class*="content"], article') or soup.body
        parrafos = [desinfectar_texto(p.text) for p in contenedor.find_all('p') if len(desinfectar_texto(p.text)) > 5]
        return {"titulo": titulo, "parrafos": parrafos, "error": None}
    except Exception as e: return {"error": str(e)}

def procesar_pdf_local(archivo_bytes, nombre_archivo):
    try:
        lector = PdfReader(io.BytesIO(archivo_bytes))
        texto = []
        for p in lector.pages:
            t = p.extract_text()
            if t: texto.extend([desinfectar_texto(l) for l in t.split('\n') if len(l.strip()) > 2])
        return {"titulo": nombre_archivo, "parrafos": texto, "error": None} if texto else {"error": "El PDF está vacío."}
    except Exception as e: return {"error": str(e)}

# --- TRADUCTOR FRACCIONADO OPTIMIZADO PARA MÓVIL ---
@st.cache_data(show_spinner=False)
def traducir_parrafos_seguro(parrafos, idioma_destino):
    parrafos_traducidos = []
    traductor = GoogleTranslator(source='auto', target=idioma_destino)
    for p in parrafos[:40]:
        if p.strip() and "[⚠️ Enlace Bloqueado]" not in p:
            try: parrafos_traducidos.append(traductor.translate(p))
            except: parrafos_traducidos.append(p)
        else:
            parrafos_traducidos.append(p)
    return parrafos_traducidos

def calcular_metricas(parrafos):
    texto_unido = " ".join(parrafos)
    palabras = len(texto_unido.split())
    return palabras, max(1, round(palabras / 250))

# --- INTERFAZ GRÁFICA PURA DE STREAMLIT ---
st.title("👑 Nexus Reader Pure Python")
st.caption("Estructura móvil de alta velocidad: Máximo rendimiento, filtros de seguridad y lectura ágil.")

# --- MENÚ LATERAL: AJUSTES DE BIBLIOTECA Y VISUALIZACIÓN ---
with st.sidebar:
    st.header("📚 Historial")
    if st.session_state.historial_urls:
        url_historial = st.selectbox("URLs recientes:", st.session_state.historial_urls)
        if st.button("Cargar desde Historial"):
            st.session_state.datos_lectura = extraer_web_optimizada(url_historial)
    else:
        st.info("Historial vacío.")

    st.divider()
    st.header("🎨 Ajustes visuales")
    modo_color = st.selectbox("Modo de Fondo:", ["☀️ Día Claro", "🍂 Sepia Confort", "🌙 Noche Profunda"])
    tamano_fuente = st.slider("Tamaño de letra:", min_value=14, max_value=32, value=18)
    
# PANEL CENTRAL: ENTRADAS DE CAPÍTULOS O ARCHIVOS
pestana_web, pestana_archivos = st.tabs(["🌐 Leer Online", "📁 Cargar PDF Local"])

with pestana_web:
    url_input = st.text_input("Inserta el enlace de la novela para leer de inmediato:", placeholder="https://")
    if st.button("🚀 Cargar Novela Online") and url_input:
        with st.spinner("Purificando texto en tiempo real..."):
            st.session_state.datos_lectura = extraer_web_optimizada(url_input)
            if url_input not in st.session_state.historial_urls:
                st.session_state.historial_urls.append(url_input)

with pestana_archivos:
    archivo_subido = st.file_uploader("Sube tu archivo PDF:", type=["pdf"])
    if archivo_subido and st.button("🛡️ Procesar PDF con Seguridad"):
        with st.spinner("Desinfectando estructura del documento..."):
            st.session_state.datos_lectura = procesar_pdf_local(archivo_subido.read(), archivo_subido.name)

# --- PANEL DE DESPLIEGUE FINAL (LECTURA FLUIDA) ---
if st.session_state.datos_lectura:
    datos = st.session_state.datos_lectura
    
    if datos.get("error"):
        st.error(f"Ocurrió un inconveniente: {datos['error']}")
    else:
        st.divider()
        
        # MOTOR NATIVO DE TRADUCCIÓN
        st.subheader("🌐 Idioma de la Obra")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            idioma_destino = st.selectbox("Traducir contenido al:", ["Idioma Original", "Español", "English", "Português"])
        with col_t2:
            st.write("") 
            if st.button("🔄 Traducir") and idioma_destino != "Idioma Original":
                with st.spinner("Traduciendo bloques..."):
                    iso_map = {"Español": "es", "English": "en", "Português": "pt"}
                    datos["parrafos"] = traducir_parrafos_seguro(datos["parrafos"], iso_map[idioma_destino])
                    st.success("¡Listo!")

        st.divider()
        
        # Módulo de estadísticas internas
        total_palabras, tiempo_estimado = calcular_metricas(datos["parrafos"])
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("📖 Palabras totales", f"{total_palabras:,}")
        col_m2.metric("⏱️ Tiempo de lectura", f"{tiempo_estimado} min")
        
        # Exportador Nativo de Streamlit
        with col_m3:
            st.download_button(
                label="📥 Descargar Texto Limpio", 
                data="\n\n".join(datos["parrafos"]), 
                file_name=f"{datos['titulo']}_purificado.txt"
            )

        st.write("---")
        st.subheader(datos["titulo"])
        
        # Control inteligente de colores
        colores_map = {
            "☀️ Día Claro": ("#FFFFFF", "#111111"),
            "🍂 Sepia Confort": ("#F5ECD5", "#433422"),
            "🌙 Noche Profunda": ("#121212", "#E0E0E0")
        }
        bg_c, text_c = colores_map[modo_color]

        html_contenedor_puro = f"""
        <div style='background-color: {bg_c}; color: {text_c}; padding: 30px; border-radius: 10px; 
                    font-size: {tamano_fuente}px; line-height: 1.8; font-family: sans-serif;'>
        """
        
        for parrafo in datos["parrafos"]:
            parrafo_seguro = parrafo.replace("<", "&lt;").replace(">", "&gt;")
            html_contenedor_puro += f"<p style='margin-bottom: 1.4em;'>{parrafo_seguro}</p>"
            
        html_contenedor_puro += "</div>"
        st.markdown(html_contenedor_puro, unsafe_allow_html=True)
