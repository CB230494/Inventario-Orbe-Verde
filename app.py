import streamlit as st
import sqlite3
import pandas as pd

# FUNCION: Conectar a la base de datos
def get_connection():
    return sqlite3.connect("inventario_orbeverde.db", check_same_thread=False)

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Inventario Orbe Verde", layout="wide")

# ESTILO NEGRO + VERDE INSTITUCIONAL
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

# DEFINIR PESTAÑAS
tabs = st.tabs(["🧑‍🍳 Cocina", "🍻 Bar", "👨‍💼 Administrador"])

# ========== 🧑‍🍳 PESTAÑA COCINA ==========
with tabs[0]:
    st.subheader("Solicitud de productos desde cocina")

    # Conexión a la base
    conn = get_connection()
    cursor = conn.cursor()

    # Cargar productos del origen 'cocina'
    productos = pd.read_sql_query(
        "SELECT id, nombre, unidad FROM productos WHERE origen = 'cocina'", conn
    )
    productos["display"] = productos["nombre"] + " (" + productos["unidad"] + ")"

    # Seleccionar múltiples productos
    seleccionados = st.multiselect("Seleccione uno o más productos", productos["display"])

    # Ingresar nombre de quien solicita
    solicitado_por = st.text_input("Solicitado por")

    # Campos dinámicos para cada producto seleccionado
    cantidades = {}
    for item in seleccionados:
        prod_id = int(productos[productos["display"] == item]["id"].values[0])
        cantidades[prod_id] = st.text_input(f"Cantidad para {item}", key=f"cantidad_{prod_id}")

    # Botón para enviar múltiples solicitudes
    if st.button("Enviar solicitud múltiple"):
        if solicitado_por and all(cantidades.values()):
            for prod_id, cant in cantidades.items():
                cursor.execute("""
                    INSERT INTO solicitudes (producto_id, cantidad, solicitado_por)
                    VALUES (?, ?, ?)
                """, (prod_id, cant, solicitado_por))
            conn.commit()
            st.success("✅ Todas las solicitudes fueron registradas correctamente.")
            st.experimental_rerun()
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
# ========== 🍻 PESTAÑA BAR ==========
with tabs[1]:
    st.subheader("Solicitud de productos desde bar")

    # Cargar productos del bar
    productos_bar = pd.read_sql_query("""
        SELECT id, nombre, marca, unidad FROM productos WHERE origen = 'bar'
    """, conn)
    productos_bar["display"] = productos_bar["nombre"] + " - " + productos_bar["marca"] + " (" + productos_bar["unidad"] + ")"

    # Selección múltiple
    seleccionados_bar = st.multiselect("Seleccione uno o más productos", productos_bar["display"])

    # Nombre de quien solicita
    solicitado_por_bar = st.text_input("Solicitado por", key="solicitado_bar")

    # Cantidades por producto seleccionado
    cantidades_bar = {}
    for item in seleccionados_bar:
        prod_id = int(productos_bar[productos_bar["display"] == item]["id"].values[0])
        cantidades_bar[prod_id] = st.text_input(f"Cantidad para {item}", key=f"cantidad_bar_{prod_id}")

    # Botón para enviar todas las solicitudes
    if st.button("Enviar solicitud múltiple desde bar"):
        if solicitado_por_bar and all(cantidades_bar.values()):
            for prod_id, cant in cantidades_bar.items():
                cursor.execute("""
                    INSERT INTO solicitudes (producto_id, cantidad, solicitado_por)
                    VALUES (?, ?, ?)
                """, (prod_id, cant, solicitado_por_bar))
            conn.commit()
            st.success("✅ Todas las solicitudes desde bar fueron registradas.")
            st.experimental_rerun()
        else:
            st.warning("⚠️ Complete todos los campos y cantidades.")

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
# ========== 👨‍💼 PESTAÑA ADMINISTRADOR ==========
with tabs[2]:
    st.subheader("Panel de control del administrador")

    st.markdown("### 🧑‍🍳 Solicitudes desde cocina")
    solicitudes_cocina = pd.read_sql_query("""
        SELECT s.id, p.nombre, s.cantidad, s.estado, s.fecha, s.solicitado_por
        FROM solicitudes s
        JOIN productos p ON s.producto_id = p.id
        WHERE p.origen = 'cocina'
        ORDER BY s.fecha DESC
    """, conn)

    for index, row in solicitudes_cocina.iterrows():
        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])
        with col1:
            st.text(f"{row['nombre']} - {row['cantidad']}")
        with col2:
            st.text(f"Solicitado por: {row['solicitado_por']}")
        with col3:
            st.text(f"Estado: {row['estado']}")
        with col4:
            if st.button("✅ Marcar", key=f"mark_cocina_{row['id']}"):
                cursor.execute("UPDATE solicitudes SET estado = 'comprado' WHERE id = ?", (row['id'],))
                conn.commit()
                st.experimental_rerun()
        with col5:
            if st.button("🗑️ Borrar", key=f"delete_cocina_{row['id']}"):
                cursor.execute("DELETE FROM solicitudes WHERE id = ?", (row['id'],))
                conn.commit()
                st.experimental_rerun()

    if st.button("🧹 Limpiar solicitudes compradas (cocina)"):
        cursor.execute("""
            DELETE FROM solicitudes
            WHERE estado = 'comprado'
            AND producto_id IN (SELECT id FROM productos WHERE origen = 'cocina')
        """)
        conn.commit()
        st.success("Solicitudes compradas eliminadas.")
        st.experimental_rerun()

    st.divider()

    st.markdown("### 🍻 Solicitudes desde bar")
    solicitudes_bar = pd.read_sql_query("""
        SELECT s.id, p.nombre, p.marca, s.cantidad, s.estado, s.fecha, s.solicitado_por
        FROM solicitudes s
        JOIN productos p ON s.producto_id = p.id
        WHERE p.origen = 'bar'
        ORDER BY s.fecha DESC
    """, conn)

    for index, row in solicitudes_bar.iterrows():
        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])
        with col1:
            st.text(f"{row['nombre']} ({row['marca']}) - {row['cantidad']}")
        with col2:
            st.text(f"Solicitado por: {row['solicitado_por']}")
        with col3:
            st.text(f"Estado: {row['estado']}")
        with col4:
            if st.button("✅ Marcar", key=f"mark_bar_{row['id']}"):
                cursor.execute("UPDATE solicitudes SET estado = 'comprado' WHERE id = ?", (row['id'],))
                conn.commit()
                st.experimental_rerun()
        with col5:
            if st.button("🗑️ Borrar", key=f"delete_bar_{row['id']}"):
                cursor.execute("DELETE FROM solicitudes WHERE id = ?", (row['id'],))
                conn.commit()
                st.experimental_rerun()

    if st.button("🧹 Limpiar solicitudes compradas (bar)"):
        cursor.execute("""
            DELETE FROM solicitudes
            WHERE estado = 'comprado'
            AND producto_id IN (SELECT id FROM productos WHERE origen = 'bar')
        """)
        conn.commit()
        st.success("Solicitudes compradas eliminadas.")
        st.experimental_rerun()
