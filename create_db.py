import mariadb
import sys
from querys import nuevo_usuario, login, actualizar_lema, actualizar_nickname, agregar_contacto, obtener_chat_usuarios
from querys import obtener_contactos_usuario, obtener_estados_contactos, obtener_lema_usuario, enviar_mensaje, agregar_estado


def conectar_mariadb():
    try:
        conn = mariadb.connect(
            user="root",
            password="1616",
            host="localhost",
            port=3306
        )
        eliminar_base_datos(conn)
        crear_base_datos(conn)
        return conn
    except mariadb.Error as e:
        print(f"Error de conexión a MariaDB: {e}")
        sys.exit(1)


def eliminar_base_datos(conn):
    try:
        cur = conn.cursor()
        cur.execute("DROP DATABASE IF EXISTS LinuxLiveMessenger")
        cur.close()
    except mariadb.Error as e:
        print(f"[Error al eliminar la base de datos: {e}]")


def crear_base_datos(conn):
    try:
        cur = conn.cursor()
        cur.execute("CREATE DATABASE LinuxLiveMessenger")
        cur.close()
    except mariadb.Error as e:
        print(f"[Error al crear la base de datos: {e}]")



def crear_tablas(conn):
    try:
        cur = conn.cursor()
        cur.execute("USE LinuxLiveMessenger")
        cur.execute("""
            CREATE TABLE Usuarios (
                id_usuario INT PRIMARY KEY AUTO_INCREMENT,
                correo_electronico VARCHAR(255) UNIQUE,
                contrasena VARCHAR(255),
                nickname VARCHAR(255),
                lema VARCHAR(255),
                foto_perfil BLOB,
                fecha_creacion TIMESTAMP
            );
        """)
        
        cur.execute("""
            CREATE TABLE Contactos (
                id_usuario INT,
                correo_electronico_contacto VARCHAR(255), 
                fecha_agregado TIMESTAMP,
                FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario),
                FOREIGN KEY (correo_electronico_contacto) REFERENCES Usuarios(correo_electronico)
            );
        """)
        
        cur.execute("""
        CREATE TABLE Estados (
            id_estado INT PRIMARY KEY AUTO_INCREMENT, 
            id_usuario INT,
            texto_estado TEXT,
            fecha_hora TIMESTAMP,
            FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario)
        );
        """)
        
        cur.execute("""
        CREATE TABLE Mensajes (
            id_mensaje INT PRIMARY KEY AUTO_INCREMENT,
            id_usuario_envia INT,
            id_usuario_recibe INT, 
            texto_mensaje TEXT,
            fecha_hora TIMESTAMP,
            FOREIGN KEY (id_usuario_envia) REFERENCES Usuarios(id_usuario),
            FOREIGN KEY (id_usuario_recibe) REFERENCES Usuarios(id_usuario)
        );
        """)
        
        # Cerrar el cursor
        cur.close()
        
    except mariadb.Error as e:
        print(Fore.LIGHTRED_EX + f"[Error al crear las tablas: {e}]")


############################################################################
        


def mostrar_contactos(conn, email):
    contactos = obtener_contactos_usuario(conn, email)
    if contactos:
        print(f"Contactos de {email}:")
        for contacto in contactos:
            print(f"- {contacto[0]} ({contacto[1]}) - Agregado: {contacto[2]}")
    else:
        print(f"El usuario {email} no tiene contactos.")



def mostar_chat(conn, email1, email2):
    mensajes = obtener_chat_usuarios(conn, email1, email2)
    if mensajes:
        for mensaje in mensajes:
            print(f"{mensaje[2]} ({mensaje[3]}): {mensaje[0]} ({mensaje[1]})")
    else:
        print(f"No hay mensajes entre {email1} y {email2}.")

############################################################################################



def poblar_tablas(conn): # Insercion de datos de prueba
    cur = conn.cursor()
    cur.execute("USE LinuxLiveMessenger")
    
    nuevo_usuario(conn, "juan@email.com", "contraseña1")
    actualizar_nickname(conn, "juan@email.com", "Juansito")

    nuevo_usuario(conn, "maria@email.com", "contraseña2")
    actualizar_nickname(conn, "maria@email.com", "Mary20")

    nuevo_usuario(conn, "eradhea@gmail.com", "password")
    actualizar_nickname(conn, "eradhea@gmail.com", "Radhe")

    agregar_contacto(conn, "juan@email.com", "eradhea@gmail.com")
    agregar_contacto(conn, "maria@email.com", "juan@email.com")
    agregar_contacto(conn, "juan@email.com", "maria@email.com")
    agregar_contacto(conn, "maria@email.com", "eradhea@gmail.com")

    agregar_estado(conn, "eradhea@gmail.com", "Qué les parece esta APP?")
    agregar_estado(conn, "maria@email.com", "Quien para hablar!? :D")
    agregar_estado(conn, "juan@email.com", "Mi gato me dijo algo muy inquietante hoy..." )

    enviar_mensaje(conn, "maria@email.com", "juan@email.com", "Hola Juan")
    enviar_mensaje(conn, "maria@email.com", "juan@email.com", "Cómo estás?")
    enviar_mensaje(conn, "juan@email.com", "maria@email.com", "Hola Maria!")
    enviar_mensaje(conn, "juan@email.com", "maria@email.com", "Bien y tú!?")
    enviar_mensaje(conn, "maria@email.com", "juan@email.com", "Bien gracias")

    actualizar_lema(conn, "eradhea@gmail.com", "El sueño de mi vida es tener el copete bien peinado")
    cur.close()





conn = conectar_mariadb()
crear_tablas(conn)
poblar_tablas(conn)
mostar_chat(conn, "juan@email.com", "maria@email.com")
print("-----------------")
mostrar_contactos(conn, "maria@email.com")
print("-------------------")
estados = obtener_estados_contactos(conn, "maria@email.com")
print(estados)
conn.close
login(conn, "eradhea@gmail.com", "password")
print("--------------------")
lema = obtener_lema_usuario(conn, "eradhea@gmail.com")
print(lema)
