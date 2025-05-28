# ------------------ Módulo Historial OPs ------------------ #
import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# Rutas de archivos
OPS_FILE = "data/ordenes_produccion.json"
USUARIOS_FILE = "data/usuarios.json"

# ------------------ Funciones auxiliares ------------------ #
def cargar_ops():
    if os.path.exists(OPS_FILE):
        with open(OPS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def get_usuario_actual():
    return st.session_state.get("usuario", None)

def cargar_usuario_info():
    if os.path.exists(USUARIOS_FILE):
        with open(USUARIOS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def get_permisos_usuario(usuario):
    usuarios = cargar_usuario_info()
    info = usuarios.get(usuario, {})
    return info.get("rol", ""), info.get("etapa_asignada", "")

def acceso_restringido(roles_permitidos):
    usuario = get_usuario_actual()
    if not usuario:
        st.warning("Inicia sesión para continuar.")
        st.stop()
    rol, _ = get_permisos_usuario(usuario)
    if rol not in roles_permitidos:
        st.warning("No tienes permiso para acceder a esta sección.")
        st.stop()

# ------------------ Módulo Historial OPs ------------------ #
def modulo_historial_ops():
    #acceso_restringido(["administrador", "planificador", "trabajador"])

    st.subheader("📚 Historial de Órdenes de Producción")

    ops = cargar_ops()
    if not ops:
        st.info("No hay datos de OPs registrados.")
        return

    filtro_fecha = st.date_input("📅 Filtrar OPs por fecha de creación (opcional)", value=None)

    historial_expandido = []

    for op in ops:
        historial = op.get("historial", [])
        if filtro_fecha:
            if not historial or 'inicio' not in historial[0]:
                continue
            fecha_inicio = datetime.fromisoformat(historial[0]["inicio"]).date()
            if fecha_inicio != filtro_fecha:
                continue

        for etapa in historial:
            inicio = etapa.get("inicio")
            fin = etapa.get("fin")
            duracion = "-"
            if inicio and fin:
                inicio_dt = datetime.fromisoformat(inicio)
                fin_dt = datetime.fromisoformat(fin)
                duracion = round((fin_dt - inicio_dt).total_seconds() / 60, 2)  # minutos

            historial_expandido.append({
                "N° OP": op["numero_op"],
                "Cliente": op["cliente"],
                "Producto": op["producto"],
                "Etapa": etapa.get("etapa"),
                "Inicio": inicio,
                "Fin": fin,
                "Duración (min)": duracion,
                "Observación": etapa.get("observacion", ""),
                "Foto": etapa.get("foto_nombre", "")
            })

    if not historial_expandido:
        st.info("No hay historial para mostrar.")
        return

    df = pd.DataFrame(historial_expandido)
    st.dataframe(df, use_container_width=True)

    # Descargar historial
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Descargar historial como CSV",
        data=csv,
        file_name="historial_op.csv",
        mime="text/csv"
    )
