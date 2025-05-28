import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# CONEXIÓN BASE DE DATOS
def get_connection():
    return sqlite3.connect("inventario_orbeverde.db", check_same_thread=False)

# CONFIGURACIÓN GENERAL
st.set_page_config(page_title="Inventario Orbe Verde", layout="wide")
st.markdown("""
    <style>
    body {
        background-color: #0e1117;
        color: white;
    }
    .main { color: white; }
    .stApp {
        background-color: #0e1117;
    }
    h1, h2, h3 {
        color: #00ff88;
    }
    </style>
""", unsafe_allow_html=True)

# LOGO Y TÍTULO
st.image("logo_orbeverde.png", width=150)  # Asegúrate que exista este archivo en tu carpeta
st.title("🍽️ Sistema de Inventario - Restaurante Orbe Verde")

# PESTAÑAS
tabs = st.tabs(["🧑‍🍳 Cocina", "🍻 Bar", "👨‍💼 Administrador"])

# ========== COCINA ==========
with tabs[0]:
    st.subheader("Solicitud de productos desde cocina")
    conn = get_connection()
    cursor = conn.cursor()

    # Cargar productos de cocina
    productos = pd.read_sql_query("SELECT id, nombre, unidad FROM productos WHERE origen = 'cocina'", conn)
    productos["display"] = productos["nombre"] + " (" + productos["unidad"] + ")"
    producto_select = st.selectbox("Seleccione un producto", productos["display"])

    cantidad = st.text_input("Cantidad solicitada")
    solicitado_por = st.text_input("Solicitado por")

    if st.button("Enviar solicitud"):
        if cantidad and solicitado_por:
            producto_id = int(productos[productos["display"] == producto_select]["id"].values[0])
            cursor.execute("""
                INSERT INTO solicitudes (producto_id, cantidad, solicitado_por)
                VALUES (?, ?, ?)
            """, (producto_id, cantidad, solicitado_por))
            conn.commit()
            st.success("✅ Solicitud registrada exitosamente.")
        else:
            st.warning("Por favor complete todos los campos.")

    st.divider()
    st.markdown("### Solicitudes recientes")
    solicitudes = pd.read_sql_query("""
        SELECT s.id, p.nombre, s.cantidad, s.estado, s.fecha, s.solicitado_por
        FROM solicitudes s
        JOIN productos p ON s.producto_id = p.id
        WHERE p.origen = 'cocina'
        ORDER BY s.fecha DESC
    """, conn)
    st.dataframe(solicitudes, use_container_width=True)

# A partir de aquí siguen las pestañas del BAR y ADMINISTRADOR...
