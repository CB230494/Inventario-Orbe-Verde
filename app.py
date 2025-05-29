import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Configuración general
st.set_page_config(page_title="Inventario Orbe Verde", layout="wide")

# Título principal
st.title("🍃 Sistema de Inventario - Restaurante Orbe Verde")

# Estilos personalizados
st.markdown(
    """
    <style>
    body { color: white; background-color: #121212; }
    .stTextInput > div > div > input,
    .stNumberInput input,
    .stDataFrame div {
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Conexión a la base de datos
conn = sqlite3.connect("inventario_orbeverde.db")
cursor = conn.cursor()

# Crear tablas si no existen
cursor.execute("""
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    categoria TEXT,
    subcategoria TEXT,
    unidad TEXT,
    tipo TEXT,
    marca TEXT,
    origen TEXT CHECK(origen IN ('cocina', 'bar')) NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS solicitudes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    producto_id INTEGER NOT NULL,
    cantidad TEXT NOT NULL,
    solicitado_por TEXT NOT NULL,
    estado TEXT DEFAULT 'pendiente',
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (producto_id) REFERENCES productos(id)
)
""")
conn.commit()

# Crear pestañas
tabs = st.tabs(["🍽 Cocina", "🍸 Bar", "🧾 Administrador"])

# ========== 🍽 PESTAÑA COCINA ==========
with tabs[0]:
    st.subheader("Solicitud de productos desde cocina")

    # Arroz → kilo
    cursor.execute("""
        UPDATE productos
        SET unidad = 'kilo'
        WHERE LOWER(nombre) = 'arroz' AND origen = 'cocina'
    """)
    conn.commit()

    # Cargar productos
    productos_cocina = pd.read_sql_query("""
        SELECT id, nombre, categoria, subcategoria, unidad
        FROM productos
        WHERE origen = 'cocina'
        ORDER BY categoria, subcategoria, nombre
    """, conn)

    solicitado_por = st.text_input("Solicitado por", key="solicitado_cocina")

    categorias = productos_cocina["categoria"].dropna().unique()
    cantidades = {}

    for cat in categorias:
        with st.expander(f"🍽 {cat}", expanded=False):
            subcategorias = productos_cocina[
                (productos_cocina["categoria"] == cat) &
                (productos_cocina["subcategoria"].notnull()) &
                (productos_cocina["subcategoria"] != "")
            ]["subcategoria"].unique()

            for sub in subcategorias:
                st.markdown(f"**{sub}**")
                sub_df = productos_cocina[
                    (productos_cocina["categoria"] == cat) &
                    (productos_cocina["subcategoria"] == sub)
                ]
                for _, row in sub_df.iterrows():
                    label = f"{row['nombre']} ({row['unidad']})"
                    key = f"cocina_{row['id']}"
                    cantidad = st.number_input(label, min_value=0, step=1, key=key)
                    if cantidad > 0:
                        cantidades[row["id"]] = cantidad

            # Otros sin subcategoría
            otros = productos_cocina[
                (productos_cocina["categoria"] == cat) &
                ((productos_cocina["subcategoria"].isnull()) | (productos_cocina["subcategoria"] == ""))
            ]
            if not otros.empty:
                st.markdown("**Otros**")
                for _, row in otros.iterrows():
                    label = f"{row['nombre']} ({row['unidad']})"
                    key = f"cocina_{row['id']}"
                    cantidad = st.number_input(label, min_value=0, step=1, key=key)
                    if cantidad > 0:
                        cantidades[row["id"]] = cantidad

    # Botón de envío
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
    st.markdown("### Solicitudes recientes de cocina")

    solicitudes_cocina = pd.read_sql_query("""
        SELECT s.id, s.producto_id, s.cantidad, s.estado, s.fecha, s.solicitado_por,
               p.nombre, p.unidad
        FROM solicitudes s
        JOIN productos p ON s.producto_id = p.id
        WHERE p.origen = 'cocina'
        ORDER BY s.fecha DESC
    """, conn)

    for _, row in solicitudes_cocina.iterrows():
        col1, col2, col3 = st.columns([3, 2, 2])
        with col1:
            st.text(f"{row['cantidad']} {row['unidad']} de {row['nombre']}")
        with col2:
            st.text(f"Solicitado por: {row['solicitado_por']}")
        with col3:
            color_estado = "#90ee90" if row["estado"] == "comprado" else "white"
            st.markdown(f"<span style='color:{color_estado};'>Estado: {row['estado']}</span>", unsafe_allow_html=True)
# ========== 🍸 PESTAÑA BAR ==========
with tabs[1]:
    st.subheader("Solicitud de productos desde bar")

    # Cargar productos de bar
    productos_bar = pd.read_sql_query("""
        SELECT id, nombre, categoria, subcategoria, unidad, marca
        FROM productos
        WHERE origen = 'bar'
        ORDER BY categoria, subcategoria, nombre
    """, conn)

    solicitado_por = st.text_input("Solicitado por", key="solicitado_bar")

    categorias_bar = productos_bar["categoria"].dropna().unique()
    cantidades_bar = {}

    for cat in categorias_bar:
        with st.expander(f"🍹 {cat}", expanded=False):

            subcategorias = productos_bar[
                (productos_bar["categoria"] == cat) &
                (productos_bar["subcategoria"].notnull()) &
                (productos_bar["subcategoria"] != "")
            ]["subcategoria"].unique()

            for sub in subcategorias:
                st.markdown(f"**{sub}**")
                sub_df = productos_bar[
                    (productos_bar["categoria"] == cat) &
                    (productos_bar["subcategoria"] == sub)
                ]
                for _, row in sub_df.iterrows():
                    label = f"{row['nombre']} ({row['marca']}) - {row['unidad']}"
                    key = f"bar_{row['id']}"
                    cantidad = st.number_input(label, min_value=0, step=1, key=key)
                    if cantidad > 0:
                        cantidades_bar[row["id"]] = cantidad

            # Otros sin subcategoría
            otros = productos_bar[
                (productos_bar["categoria"] == cat) &
                ((productos_bar["subcategoria"].isnull()) | (productos_bar["subcategoria"] == ""))
            ]
            if not otros.empty:
                st.markdown("**Otros**")
                for _, row in otros.iterrows():
                    label = f"{row['nombre']} ({row['marca']}) - {row['unidad']}"
                    key = f"bar_{row['id']}"
                    cantidad = st.number_input(label, min_value=0, step=1, key=key)
                    if cantidad > 0:
                        cantidades_bar[row["id"]] = cantidad

    # Botón de envío
    if st.button("Enviar solicitud", key="enviar_bar"):
        if solicitado_por and len(cantidades_bar) > 0:
            for prod_id, cant in cantidades_bar.items():
                cursor.execute("""
                    INSERT INTO solicitudes (producto_id, cantidad, solicitado_por)
                    VALUES (?, ?, ?)
                """, (prod_id, str(cant), solicitado_por))
            conn.commit()
            st.success("✅ Todas las solicitudes del bar fueron registradas correctamente.")
            st.rerun()
        else:
            st.warning("⚠️ Asegúrese de escribir su nombre y marcar al menos un producto con cantidad.")

    st.divider()
    st.markdown("### Solicitudes recientes del bar")

    solicitudes_bar = pd.read_sql_query("""
        SELECT s.id, s.producto_id, s.cantidad, s.estado, s.fecha, s.solicitado_por,
               p.nombre, p.unidad, p.marca
        FROM solicitudes s
        JOIN productos p ON s.producto_id = p.id
        WHERE p.origen = 'bar'
        ORDER BY s.fecha DESC
    """, conn)

    for _, row in solicitudes_bar.iterrows():
        col1, col2, col3 = st.columns([3, 2, 2])
        with col1:
            st.text(f"{row['cantidad']} {row['unidad']} de {row['nombre']} ({row['marca']})")
        with col2:
            st.text(f"Solicitado por: {row['solicitado_por']}")
        with col3:
            color_estado = "#90ee90" if row["estado"] == "comprado" else "white"
            st.markdown(f"<span style='color:{color_estado};'>Estado: {row['estado']}</span>", unsafe_allow_html=True)
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
        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 2])
        with col1:
            st.text(f"{row['cantidad']} {row['unidad']} de {row['nombre']}")
        with col2:
            st.text(f"Solicitado por: {row['solicitado_por']}")
        with col3:
            color_estado = "#90ee90" if row["estado"] == "comprado" else "white"
            st.markdown(f"<span style='color:{color_estado};'>Estado: {row['estado']}</span>", unsafe_allow_html=True)
        with col4:
            if st.button("✅ Marcar/Desmarcar", key=f"mark_cocina_{row['id']}"):
                nuevo_estado = "pendiente" if row["estado"] == "comprado" else "comprado"
                cursor.execute("UPDATE solicitudes SET estado = ? WHERE id = ?", (nuevo_estado, row['id']))
                conn.commit()
                st.rerun()
        with col5:
            if st.button("🗑️ Eliminar", key=f"delete_cocina_{row['id']}"):
                cursor.execute("DELETE FROM solicitudes WHERE id = ?", (row['id'],))
                conn.commit()
                st.rerun()

    if st.button("Actualizar", key="limpiar_cocina"):
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
        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 2])
        with col1:
            st.text(f"{row['cantidad']} {row['unidad']} de {row['nombre']} ({row['marca']})")
        with col2:
            st.text(f"Solicitado por: {row['solicitado_por']}")
        with col3:
            color_estado = "#90ee90" if row["estado"] == "comprado" else "white"
            st.markdown(f"<span style='color:{color_estado};'>Estado: {row['estado']}</span>", unsafe_allow_html=True)
        with col4:
            if st.button("✅ Marcar/Desmarcar", key=f"mark_bar_{row['id']}"):
                nuevo_estado = "pendiente" if row["estado"] == "comprado" else "comprado"
                cursor.execute("UPDATE solicitudes SET estado = ? WHERE id = ?", (nuevo_estado, row['id']))
                conn.commit()
                st.rerun()
        with col5:
            if st.button("🗑️ Eliminar", key=f"delete_bar_{row['id']}"):
                cursor.execute("DELETE FROM solicitudes WHERE id = ?", (row['id'],))
                conn.commit()
                st.rerun()

    if st.button("Actualizar", key="limpiar_bar"):
        cursor.execute("""
            DELETE FROM solicitudes
            WHERE estado = 'comprado' AND producto_id IN (
                SELECT id FROM productos WHERE origen = 'bar'
            )
        """)
        conn.commit()
        st.success("🧼 Solicitudes compradas del bar eliminadas.")
        st.rerun()



