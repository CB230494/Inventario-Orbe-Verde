import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Configuración general
st.set_page_config(page_title="Inventario Orbe Verde", layout="wide")

# Título principal
st.title("🍃 Sistema de Inventario - Restaurante Orbe Verde")

# Estilos personalizados (fondo oscuro, letras blancas)
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

# Conexión base de datos
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

    # Corregir unidad del arroz a kilo (por si no se había corregido)
    cursor.execute("""
        UPDATE productos
        SET unidad = 'kilo'
        WHERE LOWER(nombre) = 'arroz' AND origen = 'cocina'
    """)
    conn.commit()

    # Cargar productos de cocina
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

            # Subcategorías válidas
            subcategorias = productos_cocina[
                (productos_cocina["categoria"] == cat) &
                (productos_cocina["subcategoria"].notnull()) &
                (productos_cocina["subcategoria"] != "")
            ]["subcategoria"].unique()

            # Mostrar por subcategoría
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

            # Mostrar productos sin subcategoría
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
    st.markdown("### Solicitudes recientes de cocina")

    solicitudes_cocina = pd.read_sql_query("""
        SELECT s.id, s.producto_id, s.cantidad, s.estado, s.fecha, s.solicitado_por,
               p.nombre, p.unidad
        FROM solicitudes s
        JOIN productos p ON s.producto_id = p.id
        WHERE p.origen = 'cocina'
        ORDER BY s.fecha DESC
    """, conn)

    solicitudes_cocina["Producto solicitado"] = solicitudes_cocina.apply(
        lambda row: f"{row['cantidad']} {row['unidad']} de {row['nombre']}", axis=1
    )

    mostrar = solicitudes_cocina[["Producto solicitado", "estado", "fecha", "solicitado_por"]]
    st.dataframe(
        mostrar.rename(columns={
            "estado": "Estado",
            "fecha": "Fecha",
            "solicitado_por": "Solicitado por"
        }),
        use_container_width=True
    )


