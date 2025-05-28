import streamlit as st
import sqlite3
import pandas as pd

# FUNCION: Conectar a la base de datos
def get_connection():
    return sqlite3.connect("inventario_orbeverde.db", check_same_thread=False)

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Inventario Orbe Verde", layout="wide")

# ESTILO NEGRO, VERDE INSTITUCIONAL Y ENTRADAS BLANCAS
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

    # Obtener productos de cocina
    productos = pd.read_sql_query("""
        SELECT id, nombre, categoria, subcategoria, unidad
        FROM productos
        WHERE origen = 'cocina'
        ORDER BY categoria, subcategoria, nombre
    """, conn)

    # Generar display ordenado por categoría y subcategoría
    def formatear_fila(row):
        cat = f"[{row['categoria']}]"
        sub = f"({row['subcategoria']})" if row['subcategoria'] else ""
        return f"{cat} {row['nombre']} {sub} - {row['unidad']}"

    productos["display"] = productos.apply(formatear_fila, axis=1)

    seleccionados = st.multiselect("Seleccione uno o más productos", productos["display"])

    solicitado_por = st.text_input("Solicitado por")

    cantidades = {}
    for item in seleccionados:
        prod_id = int(productos[productos["display"] == item]["id"].values[0])
        cantidades[prod_id] = st.text_input(f"Cantidad para {item}", key=f"cantidad_{prod_id}")

    if st.button("Enviar solicitud múltiple"):
        if solicitado_por and all(cantidades.values()):
            for prod_id, cant in cantidades.items():
                cursor.execute("""
                    INSERT INTO solicitudes (producto_id, cantidad, solicitado_por)
                    VALUES (?, ?, ?)
                """, (prod_id, cant, solicitado_por))
            conn.commit()
            st.success("✅ Todas las solicitudes fueron registradas correctamente.")
            st.rerun()
        else:
            st.warning("⚠️ Asegúrese de llenar todos los campos y cantidades antes de enviar.")

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
