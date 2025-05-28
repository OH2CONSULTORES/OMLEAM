import streamlit as st
import sqlite3
import bcrypt

# ---------- BASE DE DATOS ----------
def init_db():
    conn = sqlite3.connect('usuarios.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            rol TEXT,
            etapa TEXT
        )
    ''')
    conn.commit()
    conn.close()

def crear_usuario_por_defecto():
    conn = sqlite3.connect('usuarios.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM usuarios")
    if c.fetchone()[0] == 0:
        hashed_password = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt())
        c.execute("INSERT INTO usuarios (username, password, rol, etapa) VALUES (?, ?, ?, ?)",
                  ("admin", hashed_password, "administrador", ""))
        conn.commit()
        print("🔐 Usuario por defecto creado: admin / admin123")
    conn.close()




def crear_usuario(username, password, rol, etapa):
    conn = sqlite3.connect('usuarios.db')
    c = conn.cursor()
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        c.execute("INSERT INTO usuarios (username, password, rol, etapa) VALUES (?, ?, ?, ?)", 
                  (username, hashed_password, rol, etapa))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verificar_usuario(username, password):
    conn = sqlite3.connect('usuarios.db')
    c = conn.cursor()
    c.execute("SELECT password, rol, etapa FROM usuarios WHERE username=?", (username,))
    result = c.fetchone()
    conn.close()
    if result:
        hashed_password, rol, etapa = result
        if bcrypt.checkpw(password.encode(), hashed_password):
            return rol, etapa
    return None, None

def obtener_usuarios():
    conn = sqlite3.connect('usuarios.db')
    c = conn.cursor()
    c.execute("SELECT id, username, rol, etapa FROM usuarios")
    users = c.fetchall()
    conn.close()
    return users

def actualizar_usuario(user_id, password=None, rol=None, etapa=None):
    conn = sqlite3.connect('usuarios.db')
    c = conn.cursor()
    if password:
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        c.execute("UPDATE usuarios SET password=? WHERE id=?", (hashed_password, user_id))
    if rol:
        c.execute("UPDATE usuarios SET rol=? WHERE id=?", (rol, user_id))
    if etapa:
        c.execute("UPDATE usuarios SET etapa=? WHERE id=?", (etapa, user_id))
    conn.commit()
    conn.close()

def eliminar_usuario(user_id):
    conn = sqlite3.connect('usuarios.db')
    c = conn.cursor()
    c.execute("DELETE FROM usuarios WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
# Fuera de login_modulo()

def registrar_usuario():
    st.subheader("➕ Crear Usuario")
    username = st.text_input("Nuevo Usuario")
    password = st.text_input("Contraseña", type="password")
    rol = st.selectbox("Rol", ["administrador", "planificador", "trabajador"])
    etapa = st.text_input("Etapa de Producción (si aplica)", placeholder="Ej: Corte, Troquelado...")
    if st.button("Crear Usuario"):
        if crear_usuario(username, password, rol, etapa):
            st.success("Usuario creado exitosamente")
        else:
            st.error("El usuario ya existe")

def administrar_usuarios():
    st.subheader("👥 Lista de Usuarios")
    usuarios = obtener_usuarios()
    for user in usuarios:
        user_id, username, rol_actual, etapa_actual = user
        with st.expander(f"👤 {username}"):
            nueva_contra = st.text_input(f"Nueva Contraseña para {username}", key=f"pwd_{user_id}", type="password")
            nuevo_rol = st.selectbox("Nuevo Rol", ["administrador", "planificador", "trabajador"],
                                     key=f"rol_{user_id}", index=["administrador", "planificador", "trabajador"].index(rol_actual))
            nueva_etapa = st.text_input("Nueva Etapa", value=etapa_actual or "", key=f"etapa_{user_id}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Actualizar", key=f"update_{user_id}"):
                    actualizar_usuario(user_id, nueva_contra if nueva_contra else None, nuevo_rol, nueva_etapa)
                    st.success("Usuario actualizado")
                    st.rerun()

            with col2:
                if username != "admin":
                    if st.button("❌ Eliminar Usuario", key=f"delete_{user_id}"):
                        eliminar_usuario(user_id)
                        st.warning(f"Usuario {username} eliminado.")
                        st.rerun()
                else:
                    st.info("Este usuario no puede eliminarse.")   
# ---------- INTERFAZ ----------
def login_modulo():
    st.markdown("<h1 style='text-align: center;'>🔐 Bienvenido a LEAN</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #007acc;'>🚀 Mejora continua al alcance de tu pantalla 💻</h3>", unsafe_allow_html=True)


    init_db()  # Inicializa la base de datos si no existe
    crear_usuario_por_defecto()  # Crea admin/admin123 si no hay usuarios

    # Crear una columna centralizada y con ancho fijo
    cols = st.columns([1, 2, 1])
    with cols[1]:
        # Usar formulario para que el botón se "presione" al hacer Enter
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            submit = st.form_submit_button("Iniciar Sesión")

            if submit:
                rol, etapa = verificar_usuario(username, password)
                if rol:
                    st.success(f"Bienvenido {username} - Rol: {rol}")
                    st.session_state['usuario'] = username
                    st.session_state['rol'] = rol
                    st.session_state['etapa'] = etapa
                    st.session_state['login'] = True
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")


