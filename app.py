import streamlit as st
import sqlite3
import pandas as pd

# Conectar a la base de datos
def get_connection():
    return sqlite3.connect("inventario_orbeverde.db", check_same_thread=False)

# Configuración general de la app
st.set_page_config(page_title="Inventario Orbe Verde", layout="wide")

# Estilo oscuro con entradas blancas
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

# Título principal
st.title("🍽️ Sistema de Inventario - Restaurante Orbe Verde")

# Crear pestañas
tabs = st.tabs(["🧑‍🍳 Cocina", "🍻 Bar", "👨‍💼 Administrador"])

# ========== 🧑‍🍳 PESTAÑA COCINA ==========
with tabs[0]:
    st.subheader("Solicitud de productos desde cocina")

    conn = get_connection()
    cursor = conn.cursor()

    # Cargar productos de cocina
    productos = pd.read_sql_query("""
        SELECT id, nombre, categoria, subcategoria, unidad
        FROM productos
        WHERE origen = 'cocina'
        ORDER BY categoria, subcategoria, nombre
    """, conn)

    solicitado_por = st.text_input("Solicitado por")

    categorias = productos["categoria"].unique()
    cantidades = {}

    # Mostrar productos por categoría
    for categoria in categorias:
        with st.expander(f"🗂️ {categoria}", expanded=False):
            subset = productos[productos["categoria"] == categoria]
            for _, row in subset.iterrows():
                label = row["nombre"]
                if row["subcategoria"]:
                    label += f" ({row['subcategoria']})"
                label += f" - {row['unidad']}"
                key = f"cocina_{row['id']}"
                cantidad = st.number_input(f"{label}", min_value=0, step=1, key=key)
                if cantidad > 0:
                    cantidades[row["id"]] = cantidad

    # Botón para enviar solicitud
    if st.button("Enviar solicitud", key="enviar_cocina"):
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

    # Mostrar solicitudes de cocina en formato mejorado
    solicitudes = pd.read_sql_query("""
        SELECT s.id, s.producto_id, s.cantidad, s.estado, s.fecha, s.solicitado_por,
               p.nombre, p.unidad
        FROM solicitudes s
        JOIN productos p ON s.producto_id = p.id
        WHERE p.origen = 'cocina'
        ORDER BY s.fecha DESC
    """, conn)

    # Crear texto formateado
    solicitudes["Producto solicitado"] = solicitudes.apply(
        lambda row: f"{row['cantidad']} {row['unidad']} de {row['nombre']}", axis=1
    )

    mostrar = solicitudes[["Producto solicitado", "estado", "fecha", "solicitado_por"]]
    st.dataframe(mostrar.rename(columns={
        "estado": "Estado",
        "fecha": "Fecha",
        "solicitado_por": "Solicitado por"
    }), use_container_width=True)
# ========== 🍻 PESTAÑA BAR ==========
with tabs[1]:
    st.subheader("Solicitud de productos desde bar")

    # Cargar productos del bar
    productos_bar = pd.read_sql_query("""
        SELECT id, nombre, tipo, marca, unidad
        FROM productos
        WHERE origen = 'bar'
        ORDER BY tipo, marca, nombre
    """, conn)

    solicitado_por_bar = st.text_input("Solicitado por", key="solicitado_bar")

    tipos = productos_bar["tipo"].unique()
    cantidades_bar = {}

    for tipo in tipos:
        with st.expander(f"🍶 {tipo}", expanded=False):
            subset = productos_bar[productos_bar["tipo"] == tipo]
            for _, row in subset.iterrows():
                label = f"{row['nombre']} - {row['marca']} ({row['unidad']})"
                key = f"bar_{row['id']}"
                cantidad = st.number_input(f"{label}", min_value=0, step=1, key=key)
                if cantidad > 0:
                    cantidades_bar[row["id"]] = cantidad

    # Botón de envío
    if st.button("Enviar solicitud", key="enviar_bar"):
        if solicitado_por_bar and len(cantidades_bar) > 0:
            for prod_id, cant in cantidades_bar.items():
                cursor.execute("""
                    INSERT INTO solicitudes (producto_id, cantidad, solicitado_por)
                    VALUES (?, ?, ?)
                """, (prod_id, str(cant), solicitado_por_bar))
            conn.commit()
            st.success("✅ Todas las solicitudes desde bar fueron registradas correctamente.")
            st.rerun()
        else:
            st.warning("⚠️ Asegúrese de escribir su nombre y marcar al menos un producto con cantidad.")

    st.divider()
    st.markdown("### Solicitudes recientes del bar")

    # Mostrar solicitudes formateadas
    solicitudes_bar = pd.read_sql_query("""
        SELECT s.id, s.producto_id, s.cantidad, s.estado, s.fecha, s.solicitado_por,
               p.nombre, p.unidad, p.marca
        FROM solicitudes s
        JOIN productos p ON s.producto_id = p.id
        WHERE p.origen = 'bar'
        ORDER BY s.fecha DESC
    """, conn)

    solicitudes_bar["Producto solicitado"] = solicitudes_bar.apply(
        lambda row: f"{row['cantidad']} {row['unidad']} de {row['nombre']} ({row['marca']})", axis=1
    )

    mostrar_bar = solicitudes_bar[["Producto solicitado", "estado", "fecha", "solicitado_por"]]
    st.dataframe(mostrar_bar.rename(columns={
        "estado": "Estado",
        "fecha": "Fecha",
        "solicitado_por": "Solicitado por"
    }), use_container_width=True)
# ========== 👨‍💼 PESTAÑA ADMINISTRADOR ==========
with tabs[2]:
    st.subheader("Panel de control del administrador")

    # ----- COCINA -----
    st.markdown("### 🧑‍🍳 Solicitudes desde cocina")

    solicitudes_cocina = pd.read_sql_query("""
        SELECT s.id, s.producto_id, s.cantidad, s.estado, s.fecha, s.solicitado_por,
               p.nombre, p.unidad
        FROM solicitudes s
        JOIN productos p ON s.producto_id = p.id
        WHERE p.origen = 'cocina'
        ORDER BY s.fecha DESC
    """, conn)

    for index, row in solicitudes_cocina.iterrows():
        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])
        with col1:
            st.text(f"{row['cantidad']} {row['unidad']} de {row['nombre']}")
        with col2:
            st.text(f"Solicitado por: {row['solicitado_por']}")
        with col3:
            st.text(f"Estado: {row['estado']}")
        with col4:
            if st.button("✅", key=f"mark_cocina_{row['id']}"):
                nuevo_estado = "pendiente" if row["estado"] == "comprado" else "comprado"
                cursor.execute("UPDATE solicitudes SET estado = ? WHERE id = ?", (nuevo_estado, row['id']))
                conn.commit()
                st.rerun()
        with col5:
            if st.button("🗑️", key=f"delete_cocina_{row['id']}"):
                cursor.execute("DELETE FROM solicitudes WHERE id = ?", (row['id'],))
                conn.commit()
                st.rerun()

    if st.button("Enviar solicitud", key="limpiar_cocina"):
        cursor.execute("""
            DELETE FROM solicitudes
            WHERE estado = 'comprado' AND producto_id IN (
                SELECT id FROM productos WHERE origen = 'cocina'
            )
        """)
        conn.commit()
        st.success("🧼 Solicitudes compradas de cocina eliminadas.")
        st.rerun()

    st.divider()

    # ----- BAR -----
    st.markdown("### 🍻 Solicitudes desde bar")

    solicitudes_bar = pd.read_sql_query("""
        SELECT s.id, s.producto_id, s.cantidad, s.estado, s.fecha, s.solicitado_por,
               p.nombre, p.unidad, p.marca
        FROM solicitudes s
        JOIN productos p ON s.producto_id = p.id
        WHERE p.origen = 'bar'
        ORDER BY s.fecha DESC
    """, conn)

    for index, row in solicitudes_bar.iterrows():
        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])
        with col1:
            st.text(f"{row['cantidad']} {row['unidad']} de {row['nombre']} ({row['marca']})")
        with col2:
            st.text(f"Solicitado por: {row['solicitado_por']}")
        with col3:
            st.text(f"Estado: {row['estado']}")
        with col4:
            if st.button("✅", key=f"mark_bar_{row['id']}"):
                nuevo_estado = "pendiente" if row["estado"] == "comprado" else "comprado"
                cursor.execute("UPDATE solicitudes SET estado = ? WHERE id = ?", (nuevo_estado, row['id']))
                conn.commit()
                st.rerun()
        with col5:
            if st.button("🗑️", key=f"delete_bar_{row['id']}"):
                cursor.execute("DELETE FROM solicitudes WHERE id = ?", (row['id'],))
                conn.commit()
                st.rerun()

    if st.button("Enviar solicitud", key="limpiar_bar"):
        cursor.execute("""
            DELETE FROM solicitudes
            WHERE estado = 'comprado' AND producto_id IN (
                SELECT id FROM productos WHERE origen = 'bar'
            )
        """)
        conn.commit()
        st.success("🧼 Solicitudes compradas del bar eliminadas.")
        st.rerun()


