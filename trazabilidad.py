import streamlit as st
import pandas as pd
import os
import json
import matplotlib.pyplot as plt

TRAZABILIDAD_FILE = "data/trazabilidad.json"

def cargar_trazabilidad():
    if os.path.exists(TRAZABILIDAD_FILE):
        with open(TRAZABILIDAD_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return pd.DataFrame(data)
    else:
        return pd.DataFrame()

def mostrar_trazabilidad():
    st.title("🔍 Trazabilidad de Órdenes de Producción")

    df_trazabilidad = cargar_trazabilidad()

    if df_trazabilidad.empty:
        st.info("No hay datos de trazabilidad disponibles.")
        return

    # Mostrar tabla completa
    st.subheader("📋 Historial completo")
    st.dataframe(df_trazabilidad)

    # Filtrado por OP
    op_unicas = df_trazabilidad["op"].unique()
    op_seleccionada = st.selectbox("🔎 Filtrar por OP", options=op_unicas)
    df_op = df_trazabilidad[df_trazabilidad["op"] == op_seleccionada]

    st.subheader(f"📌 Detalles de la OP: {op_seleccionada}")
    st.dataframe(df_op)

        # Mostrar imágenes si hay fotos asociadas
    st.subheader("🖼️ Evidencia fotográfica por etapa")

    fotos_disponibles = df_op.dropna(subset=["foto_nombre"])

    for idx, row in fotos_disponibles.iterrows():
        ruta_foto = f"data/fotos/{row['foto_nombre']}"
        if os.path.exists(ruta_foto):
            st.markdown(f"**Etapa:** {row['etapa_nueva']} — **Comentario:** {row['comentario']}")
            st.image(ruta_foto, width=200)
        else:
            st.warning(f"Foto no encontrada: {row['foto_nombre']}")

    # Mostrar tiempos de estadía por etapa
    if "tiempo_estadia_min" in df_op.columns:
        st.subheader("⏱️ Tiempo de estadía por etapa (minutos)")
        tiempos = df_op[["etapa_nueva", "tiempo_estadia_min"]].dropna()
        st.dataframe(tiempos)

        fig2, ax2 = plt.subplots()
        ax2.bar(tiempos["etapa_nueva"], tiempos["tiempo_estadia_min"], color="orange")
        ax2.set_ylabel("Minutos")
        ax2.set_title("Tiempo de Estadía por Etapa")
        ax2.tick_params(axis='x', rotation=45)
        st.pyplot(fig2)






    # Normalizar columna datos_etapa
    if 'datos_etapa' in df_trazabilidad.columns:
        datos_etapa_df = pd.json_normalize(df_trazabilidad['datos_etapa'])
        df_expandido = pd.concat([df_trazabilidad.drop(columns=['datos_etapa']), datos_etapa_df], axis=1)

        # Asegurar tipo datetime
        df_expandido['fecha'] = pd.to_datetime(df_expandido['fecha'], errors='coerce')

        # Verificar que 'etapa_nueva' y 'tiempo_total' existan
        if 'etapa_nueva' in df_expandido.columns and 'tiempo_total' in df_expandido.columns:
            tiempos_por_etapa = df_expandido.groupby('etapa_nueva')['tiempo_total'].mean().reset_index()

            # Graficar
            st.subheader("⏱️ Tiempo promedio por etapa")
            fig, ax = plt.subplots()
            ax.bar(tiempos_por_etapa['etapa_nueva'], tiempos_por_etapa['tiempo_total'], color='skyblue')
            ax.set_xlabel("Etapa")
            ax.set_ylabel("Tiempo Promedio (minutos)")
            ax.set_title("Tiempo Promedio por Etapa")
            ax.tick_params(axis='x', rotation=45)
            st.pyplot(fig)
        else:
            st.warning("Faltan columnas necesarias para graficar.")
    else:
        st.warning("No se encuentra la columna 'datos_etapa'.")
