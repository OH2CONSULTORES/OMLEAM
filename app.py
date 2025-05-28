import streamlit as st
import login
import etapas
import crear_op
import kanban
import historial
import json
import os
import alertas

st.set_page_config(
    page_title="OmLean - Sistema Kanban",
    page_icon="🏭",  # Puedes usar un emoji o una imagen .ico/.png (ver abajo)
    layout="wide"
)

# Título y frase
#st.markdown("<h1 style='text-align: center; color: #004080;'>OmLean - Sistema Kanban</h1>", unsafe_allow_html=True)
#st.markdown("<h4 style='text-align: center; color: gray;'>Optimiza tu producción con herramientas Lean Manufacturing</h4>", unsafe_allow_html=True)


ALERTAS_FILE = "data/alertas_pendientes.json"
OPS_FILE = "data/ordenes_produccion.json"

def mostrar_usuario_rol_logout():
    # Contenedor con ancho limitado usando columnas
    col1, col2 = st.sidebar.columns([3,1])  # Col1 ancho mayor, col2 para botón pequeño

    with col1:
        st.markdown("### 👤")
        st.write(f"**Usuario:** {st.session_state['usuario']}")
        st.write(f"**Rol:** {st.session_state['rol']}")
        st.write(f"**Etapa:** {st.session_state['etapa']}")

    with col2:
        if st.button("🔚"):
            st.session_state.clear()
            st.rerun()

def cargar_ops():
    if os.path.exists(OPS_FILE):
        with open(OPS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []





# Inicio sesión
if 'login' not in st.session_state or not st.session_state['login']:
    login.login_modulo()
else:
    mostrar_usuario_rol_logout()
    alertas.mostrar_notificaciones(st.session_state['usuario'])  # <- NUEVO

    tabs = st.tabs(["⚙️ Etapas", "➕ Crear OP", "📊 Kanban", "📁 Historial", "👥 Usuarios"])

    with tabs[0]:
        if st.session_state['rol'] in ["administrador", "planificador"]:
            etapas.modulo_etapas()
        else:
            st.warning("No tienes permiso para ver esta sección.")

    with tabs[1]:
        if st.session_state['rol'] in ["administrador", "planificador"]:
            crear_op.crear_op()
            # Por ejemplo, después de crear OP, agregar notificación:
            # st.session_state.setdefault('notificaciones', []).append("Se creó una nueva OP")
        else:
            st.warning("No tienes permiso para ver esta sección.")

    with tabs[2]:
        if st.session_state['rol'] in ["administrador", "planificador"]:
            kanban.tablero_kanban()
        else:
            st.warning("No tienes permiso para ver esta sección.")
        

    with tabs[3]:
        if st.session_state['rol'] in ["administrador", "planificador"]:
            historial.modulo_historial_ops()
        else:
            st.warning("No tienes permiso para ver esta sección.")

    with tabs[4]:
        if st.session_state['rol'] == "administrador":
            login.registrar_usuario()
            login.administrar_usuarios()
        else:
            st.warning("No tienes permiso para ver esta sección.")
