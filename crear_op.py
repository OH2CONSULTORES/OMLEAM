import streamlit as st
import json
import os
from datetime import datetime, date
from PIL import Image
import fitz  # PyMuPDF para convertir PDF a imagen

ETAPAS_FILE = "data/etapas.json"
OPS_FILE = "data/ordenes_produccion.json"
IMAGENES_DIR = "files/imagenes_op"

os.makedirs(IMAGENES_DIR, exist_ok=True)

def cargar_etapas():
    if os.path.exists(ETAPAS_FILE):
        with open(ETAPAS_FILE, "r") as f:
            return json.load(f)
    return []

def cargar_ops():
    if os.path.exists(OPS_FILE):
        with open(OPS_FILE, "r") as f:
            return json.load(f)
    return []

def guardar_ops(ops):
    with open(OPS_FILE, "w") as f:
        json.dump(ops, f, indent=4)

def guardar_pdf_como_imagen(pdf_file, nombre_archivo_imagen):
    try:
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        page = doc.load_page(0)  # primera página
        pix = page.get_pixmap(dpi=150)
        ruta_imagen = os.path.join(IMAGENES_DIR, nombre_archivo_imagen)
        pix.save(ruta_imagen)
        return ruta_imagen
    except Exception as e:
        st.error(f"Error al convertir PDF con fitz: {e}")
    return None

def crear_op():
    st.subheader("🆕 Crear Orden de Producción (OP)")

    etapas_disponibles = cargar_etapas()
    nombres_etapas_disponibles = [e["nombre"] for e in etapas_disponibles]

    etapas_default = ["En Cola", "Transporte", "OP Terminados"]
    etapas_validas = [etapa for etapa in etapas_default if etapa in nombres_etapas_disponibles]






    with st.form("form_crear_op"):
        col1, col2, col3 = st.columns(3)
        with col1:
            numero_op = st.text_input("Número de OP")
        with col2:
            cliente = st.text_input("Cliente")
        with col3:
            producto = st.text_input("Producto")

        col4, col5 = st.columns([1, 1.5])
        with col4:
            cantidad = st.number_input("Cantidad", min_value=1)
        with col5:
            fecha_entrega = st.date_input("Fecha estimada de entrega", min_value=date.today())

        dias_restantes = (fecha_entrega - date.today()).days
        st.info(f"📅 Faltan **{dias_restantes} días** para la entrega.")

        etapas_seleccionadas = st.multiselect(
            "Selecciona las etapas por las que pasará esta OP",
            nombres_etapas_disponibles,
            default=etapas_validas
        )

        archivo_pdf = st.file_uploader("📄 Cargar documento PDF asociado", type=["pdf"])

        submitted = st.form_submit_button("Crear OP")

        if submitted:
            if not numero_op or not cliente or not producto or not etapas_seleccionadas:
                st.warning("Por favor, completa todos los campos.")
                return

            ops = cargar_ops()
            if any(op["numero_op"] == numero_op for op in ops):
                st.error("Ya existe una OP con ese número.")
                return

            imagen_path = None
            if archivo_pdf:
                nombre_archivo = f"{numero_op}_{producto.replace(' ', '_')}.png"
                imagen_path = guardar_pdf_como_imagen(archivo_pdf, nombre_archivo)
                st.write(f"Imagen guardada en: {imagen_path}")

            now = datetime.now().isoformat()
            nueva_op = {
                "numero_op": numero_op,
                "cliente": cliente,
                "producto": producto,
                "cantidad": cantidad,
                "fecha_entrega": fecha_entrega.isoformat(),
                "dias_restantes": dias_restantes,
                "etapas": etapas_seleccionadas,
                "estado_actual": etapas_seleccionadas[0],
                "planificacion": {},
                "historial": [
                    {
                        "etapa": etapas_seleccionadas[0],
                        "inicio": now,
                        "fin": None,
                        "observacion": None
                    }
                ],
                "imagen_op": imagen_path
            }

            ops.append(nueva_op)
            guardar_ops(ops)
            st.success(f"✅ OP {numero_op} creada correctamente.")

# Para usar la función en una app principal de Streamlit, basta con llamar:
# crear_op()