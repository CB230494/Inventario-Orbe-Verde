import streamlit as st
import sqlite3
import pandas as pd

# CONEXIÓN BASE DE DATOS
def get_connection():
    return sqlite3.connect("inventario_orbeverde.db", check_same_thread=False)

# CONFIGURACIÓN GENERAL DE PÁGINA
st.set_page_config(page_title="Inventario Orbe Verde", layout="wide")

# ESTILOS: NEGRO + VERDE INSTITUCIONAL + TEXTO BLANCO
st.markdown("""
    <style>
    body { background-color: #0e1117; color: white; }
    .main { color: white; }
    .stApp { background-color: #0e1117; }
    h1, h2, h3, .st-bb { color: #00ff88; }
    </style>
""", unsafe_allow_html=True)

# TÍTULO PRINCIPAL
st.title("🍽️ Sistema de Inventario - Restaurante Orbe Verde")

# PESTAÑAS
tabs = st.tabs(["🧑‍🍳 Cocina", "🍻 Bar", "👨‍💼 Administrador"])

# ========== COCINA ==========
with tabs[0]:
    st.subheader("Solicitud de productos desde cocina")
    
    conn = get_connection()
    cursor = conn.cursor()

    # Cargar productos disponibles de cocina
    productos = pd.read_sql_query(
        "SELECT id, nombre, unidad FROM productos WHERE origen = 'cocina'",
        conn
    )
    productos["display"] = productos["nombre"] + " (" + productos["unidad"] + ")"

    # Formulario de solicitud
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
with tabs[1]:
    st.subheader("Solicitud de productos desde bar")

    # Cargar productos disponibles del bar
    productos_bar = pd.read_sql_query(
        "SELECT id, nombre, marca, unidad FROM productos WHERE origen = 'bar'",
        conn
    )
    productos_bar["display"] = productos_bar["nombre"] + " - " + productos_bar["marca"] + " (" + productos_bar["unidad"] + ")"

    producto_select_bar = st.selectbox("Seleccione un producto", productos_bar["display"])
    cantidad_bar = st.text_input("Cantidad solicitada", key="cantidad_bar")
    solicitado_por_bar = st.text_input("Solicitado por", key="solicitado_por_bar")

    if st.button("Enviar solicitud desde bar"):
        if cantidad_bar and solicitado_por_bar:
            producto_id = int(productos_bar[productos_bar["display"] == producto_select_bar]["id"].values[0])
            cursor.execute("""
                INSERT INTO solicitudes (producto_id, cantidad, solicitado_por)
                VALUES (?, ?, ?)
            """, (producto_id, cantidad_bar, solicitado_por_bar))
            conn.commit()
            st.success("✅ Solicitud desde bar registrada.")
        else:
            st.warning("Por favor complete todos los campos.")

    st.divider()
    st.markdown("### Solicitudes recientes del bar")
    solicitudes_bar = pd.read_sql_query("""
        SELECT s.id, p.nombre, p.marca, s.cantidad, s.estado, s.fecha, s.solicitado_por
        FROM solicitudes s
        JOIN productos p ON s.producto_id = p.id
        WHERE p.origen = 'bar'
        ORDER BY s.fecha DESC
    """, conn)
    st.dataframe(solicitudes_bar, use_container_width=True)

