import streamlit as st
import sqlite3
import pandas as pd

# FUNCION: Conectar a la base de datos
def get_connection():
    return sqlite3.connect("inventario_orbeverde.db", check_same_thread=False)

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Inventario Orbe Verde", layout="wide")

# ESTILO OSCURO Y CAMPOS BLANCOS
st.markdown("""
    <style>
    body { background-color: #0e1117; color: white; }
    .main { color: white; }
    .stApp { background-color: #0e1117; }
    h1, h2, h3, .st-bb { color: #00ff88; }
    input, select, textarea {
        background-color: #1a1d26 !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# TÍTULO
st.title("🍽️ Sistema de Inventario - Restaurante Orbe Verde")

# TABS
tabs = st.tabs(["🧑‍🍳 Cocina", "🍻 Bar", "👨‍💼 Administrador"])

# ========== 🧑‍🍳 PESTAÑA COCINA ==========
with tabs[0]:
    st.subheader("Solicitud de productos desde cocina")

    conn = get_connection()
    cursor = conn.cursor()

    # Obtener productos de cocina organizados
    productos = pd.read_sql_query("""
        SELECT id, nombre, categoria, subcategoria, unidad
        FROM productos
        WHERE origen = 'cocina'
        ORDER BY categoria, subcategoria, nombre
    """, conn)

    solicitado_por = st.text_input("Solicitado por")

    # Agrupar por categoría
    categorias = productos["categoria"].unique()
    cantidades = {}

    for categoria in categorias:
        with st.expander(f"🗂️ {categoria}", expanded=False):
            subset = productos[productos["categoria"] == categoria]
            for _, row in subset.iterrows():
                label = row["nombre"]
                if row["subcategoria"]:
                    label += f" ({row['subcategoria']})"
                label += f" - {row['unidad']}"
                key = f"cocina_{row['id']}"
                cantidad = st.number_input(f"{label}", min_value=0.0, step=0.5, key=key)
                if cantidad > 0:
                    cantidades[row["id"]] = cantidad

    if st.button("Enviar solicitud múltiple"):
        if solicitado_por and len(cantidades) > 0:
            for prod_id, cant in cantidades.items():
                cursor.execute("""
                    INSERT INTO solicitudes (producto_id, cantidad, solicitado_por)
                    VALUES (?, ?, ?)
                """, (prod_id, str(cant), solicitado_por))
            conn.commit()
            st.success("✅ Todas las solicitudes fueron registradas correctamente.")
            st.rerun()
        else:
            st.warning("⚠️ Asegúrese de escribir su nombre y marcar al menos un producto con cantidad.")

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

