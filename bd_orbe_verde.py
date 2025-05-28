import sqlite3

# Crear o conectar a la base de datos
conn = sqlite3.connect("inventario_orbeverde.db")
cursor = conn.cursor()

# TABLA: Productos generales (cocina + bar)
cursor.execute("""
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    categoria TEXT NOT NULL,
    subcategoria TEXT,
    tipo TEXT,            -- Usado para bebidas (Cerveza, Licor, etc.)
    marca TEXT,           -- Solo se aplica a productos del bar
    unidad TEXT NOT NULL,
    origen TEXT NOT NULL  -- 'cocina' o 'bar'
)
""")

# TABLA: Solicitudes generales (cocina + bar)
cursor.execute("""
CREATE TABLE IF NOT EXISTS solicitudes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    producto_id INTEGER NOT NULL,
    cantidad TEXT NOT NULL,
    estado TEXT DEFAULT 'pendiente',
    fecha TEXT DEFAULT CURRENT_TIMESTAMP,
    solicitado_por TEXT,
    FOREIGN KEY (producto_id) REFERENCES productos(id)
)
""")

# =========================
# INSERTAR PRODUCTOS COCINA
# =========================
productos_cocina = [
    # Verduras y Hortalizas
    ("Plátano verde", "Verduras y Hortalizas", "Plátano", None, None, "unidad", "cocina"),
    ("Chayote", "Verduras y Hortalizas", None, None, None, "unidad", "cocina"),
    ("Chile dulce", "Verduras y Hortalizas", "Chile", None, None, "unidad", "cocina"),
    ("Culantro", "Verduras y Hortalizas", "Rollos de culantro", None, None, "rollo", "cocina"),
    ("Culantro coyote", "Verduras y Hortalizas", None, None, None, "manojo", "cocina"),
    ("Repollo", "Verduras y Hortalizas", None, None, None, "unidad", "cocina"),
    ("Aguacate", "Verduras y Hortalizas", None, None, None, "unidad", "cocina"),
    ("Cebollino", "Verduras y Hortalizas", None, None, None, "manojo", "cocina"),
    ("Cebolla morada", "Verduras y Hortalizas", None, None, None, "unidad", "cocina"),
    ("Trenza de cebolla", "Verduras y Hortalizas", None, None, None, "trenza", "cocina"),
    ("Ajo", "Verduras y Hortalizas", "Maya/Trenza de Ajo", None, None, "unidad", "cocina"),
    ("Papa", "Verduras y Hortalizas", None, None, None, "kg", "cocina"),
    ("Brócoli", "Verduras y Hortalizas", None, None, None, "unidad", "cocina"),
    ("Zucchini", "Verduras y Hortalizas", None, None, None, "unidad", "cocina"),
    ("Lechuga", "Verduras y Hortalizas", None, None, None, "unidad", "cocina"),
    ("Rábano", "Verduras y Hortalizas", None, None, None, "unidad", "cocina"),
    ("Tomate", "Verduras y Hortalizas", None, None, None, "kg", "cocina"),
    ("Pepino", "Verduras y Hortalizas", None, None, None, "unidad", "cocina"),
    ("Zanahoria", "Verduras y Hortalizas", None, None, None, "unidad", "cocina"),
    ("Vainica", "Verduras y Hortalizas", None, None, None, "½ kg", "cocina"),
    ("Elote", "Verduras y Hortalizas", None, None, None, "unidad", "cocina"),
    ("Albahaca", "Verduras y Hortalizas", None, None, None, "manojo", "cocina"),
    ("Perejil", "Verduras y Hortalizas", None, None, None, "manojo", "cocina"),

    # Proteínas
    ("Filete de pescado", "Proteínas", None, None, None, "caja", "cocina"),
    ("Pechuga de pollo", "Proteínas", None, None, None, "kg", "cocina"),
    ("Carne para mechar", "Proteínas", None, None, None, "kg", "cocina"),
    ("Carne molida", "Proteínas", None, None, None, "kg", "cocina"),
    ("Alitas de pollo", "Proteínas", None, None, None, "paquete", "cocina"),
    ("Jamón", "Proteínas", None, None, None, "unidad", "cocina"),
    ("Salchichón", "Proteínas", None, None, None, "kg", "cocina"),
    ("Huevos", "Proteínas", None, None, None, "cartón (15)", "cocina"),
    ("Queso amarillo", "Proteínas", None, None, None, "kg", "cocina"),
    ("Queso mozarella", "Proteínas", "Laminado", None, None, "paquete", "cocina"),

    # Productos Secos
    ("Frijoles de chifrijo", "Productos secos", None, None, None, "paquete", "cocina"),
    ("Arroz", "Productos secos", None, None, None, "paquete", "cocina"),
    ("Harina", "Productos secos", None, None, None, "kg", "cocina"),
    ("Tortilla de chalupa", "Productos secos", None, None, None, "paquete", "cocina"),
    ("Tortilla para birria", "Productos secos", None, None, None, "paquete", "cocina"),
    ("Tortilla campesina", "Productos secos", None, None, None, "paquete", "cocina"),
    ("Pasta para chifrijón", "Productos secos", None, None, None, "paquete", "cocina"),
    ("Pan hamburguesa grande", "Productos secos", None, None, None, "paquete", "cocina"),
    ("Empanizador", "Productos secos", None, None, None, "paquete", "cocina"),

    # Bebidas y Lácteos
    ("Leche", "Bebidas y Lácteos", None, None, None, "galón", "cocina"),
    ("Jugo de limón", "Bebidas y Lácteos", None, None, None, "galón", "cocina"),

    # Salsas y Condimentos
    ("Aceite de cocina", "Salsas y Condimentos", None, None, None, "litro", "cocina"),
    ("Salsa de tomate", "Salsas y Condimentos", None, None, None, "galón", "cocina"),
    ("Mayonesa", "Salsas y Condimentos", None, None, None, "galón", "cocina"),
    ("Mostaza", "Salsas y Condimentos", None, None, None, "botella", "cocina"),
    ("Salsa tártara", "Salsas y Condimentos", None, None, None, "botella", "cocina"),
    ("Ginger", "Salsas y Condimentos", None, None, None, "unidad", "cocina"),
    ("Sal fina", "Salsas y Condimentos", None, None, None, "salero", "cocina"),

    # Limpieza y Empaque
    ("Toalla de cocina", "Limpieza y Empaque", None, None, None, "unidad", "cocina"),
    ("Empaques de comida", "Limpieza y Empaque", None, None, None, "paquete", "cocina"),
    ("Bolsas para apretadas", "Limpieza y Empaque", None, None, None, "paquete", "cocina"),
    ("Lava platos", "Limpieza y Empaque", None, None, None, "botella", "cocina"),
    ("Gas", "Limpieza y Empaque", None, None, None, "cilindro", "cocina")
]

# ======================
# INSERTAR PRODUCTOS BAR
# ======================
productos_bar = [
    ("Cerveza", "Bebidas alcohólicas", None, "Cerveza", "Imperial", "botella", "bar"),
    ("Cerveza", "Bebidas alcohólicas", None, "Cerveza", "Pilsen", "botella", "bar"),
    ("Cerveza", "Bebidas alcohólicas", None, "Cerveza", "Bavaria", "botella", "bar"),
    ("Cerveza", "Bebidas alcohólicas", None, "Cerveza", "Rock Ice", "botella", "bar"),
    ("Cerveza", "Bebidas alcohólicas", None, "Cerveza", "Heineken", "botella", "bar"),
    ("Guaro", "Bebidas alcohólicas", None, "Licor", "Cacique", "botella", "bar"),
    ("Ron", "Bebidas alcohólicas", None, "Licor", "Ron Centenario", "botella", "bar"),
    ("Tequila", "Bebidas alcohólicas", None, "Licor", "José Cuervo", "botella", "bar"),
    ("Vodka", "Bebidas alcohólicas", None, "Licor", "Smirnoff", "botella", "bar"),
    ("Whisky", "Bebidas alcohólicas", None, "Licor", "Old Parr", "botella", "bar"),
    ("Whisky", "Bebidas alcohólicas", None, "Licor", "Jack Daniel’s", "botella", "bar"),
    ("Sangría", "Bebidas alcohólicas", None, "Vino", "Sangría Tropical", "botella", "bar"),
    ("Vino Tinto", "Bebidas alcohólicas", None, "Vino", "Concha y Toro", "botella", "bar"),
    ("Vino Blanco", "Bebidas alcohólicas", None, "Vino", "Gato Negro", "botella", "bar"),
    ("Refresco", "Bebidas no alcohólicas", None, "Natural", "Fresco natural", "litro", "bar"),
    ("Jugo", "Bebidas no alcohólicas", None, "Natural", "Jugo de frutas", "litro", "bar"),
    ("Agua", "Bebidas no alcohólicas", None, "Botella", "Agua embotellada", "botella", "bar"),
    ("Hielo", "Insumo", None, "Insumo", "Hielo picado", "bolsa", "bar"),
    ("Tónica", "Mezclador", None, "Mezclador", "Agua tónica", "botella", "bar"),
    ("Soda", "Mezclador", None, "Mezclador", "Soda en lata", "lata", "bar")
]

# Insertar todos los productos (cocina y bar)
for p in productos_cocina + productos_bar:
    cursor.execute("""
        INSERT INTO productos (nombre, categoria, subcategoria, tipo, marca, unidad, origen)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, p)

conn.commit()
conn.close()
