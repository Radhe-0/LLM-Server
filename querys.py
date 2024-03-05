import mariadb
import sys
import datetime
from termcolor import colored
from colorama import init, Fore, Back, Style
import passlib.hash


def respuesta_mariadb(mensaje='', error='', accion=''):
    if error == '':
        print(Fore.CYAN + Style.BRIGHT + f"Mariadb ({accion}): " + Style.RESET_ALL + Fore.RESET + mensaje)
    else:
        print(Fore.LIGHTRED_EX + Style.BRIGHT + f"Mariadb error ({accion}): " + Style.RESET_ALL + Fore.RESET + str(error))


def conectar_mariadb():
    try:
        conn = mariadb.connect(
            user="root",
            password="1616",
            host="localhost",
            port=3306
        )
        return conn
    except mariadb.Error as e:
        respuesta_mariadb(error=e, accion="conectar mariadb 1")
        sys.exit(1)


def nuevo_usuario(conn, correo_electronico, contrasena):
    try:
        cur = conn.cursor()
        cur.execute('USE LinuxLiveMessenger')
        cur.execute("SELECT correo_electronico FROM Usuarios WHERE correo_electronico = %s", (correo_electronico,))
        salida = cur.fetchone()

        if salida != None:
            respuesta_mariadb(error="El correo electrónico ya está registrado.", accion="Nuevo usuario 1")
            return False

        cur.execute("INSERT INTO Usuarios (correo_electronico, contrasena, fecha_creacion) VALUES (%s, %s, %s)", 
                    (correo_electronico, contrasena, datetime.datetime.now()))
        conn.commit()
        cur.close()
        
        respuesta_mariadb("Usuario registrado correctamente.", accion="Nuevo usuario 2")
        return True
        
    except mariadb.Error as e:
        respuesta_mariadb(error=e, accion="Nuevo usuario 3")
        return False


def login(conn, correo_electronico, contrasena):
    try:
        cur = conn.cursor()
        cur.execute("USE LinuxLiveMessenger")
        cur.execute("""
            SELECT correo_electronico, contrasena
            FROM Usuarios
            WHERE correo_electronico = %s AND contrasena = %s
        """, (correo_electronico, contrasena))
        resultado = cur.fetchone()
        cur.close()

        if resultado is None:
            respuesta_mariadb(error="Email o contraseña inválido", accion="Login 1")
            return False

        else:
            respuesta_mariadb("Inicio de sesión correcto.", accion="Login 2")
            return True

    except mariadb.Error as e:
        respuesta_mariadb(error=e, accion="Login 3")
        return False


def obtener_nickname_usuario(conn, email):
    try:
        cur = conn.cursor()
        cur.execute("USE LinuxLiveMessenger")
        cur.execute("""
                  SELECT nickname
                  FROM Usuarios
                  WHERE correo_electronico = %s
                    """, (email,))
        resultado = cur.fetchone()
        cur.close()
        if resultado:
            respuesta_mariadb("Nickname obtenido", accion="Obtener nickname 1")
            return resultado[0]
        else:
            respuesta_mariadb(error="No hubo resultado", accion="Obtener nickname 2")
            return None
    except mariadb.Error as e:
        respuesta_mariadb(error=e, accion="Obtener nickname 3")
        return None



def actualizar_nickname(conn, correo_electronico, nickname):
    try:
        cur = conn.cursor()
        cur.execute("SELECT id_usuario FROM Usuarios WHERE correo_electronico = %s", (correo_electronico,))
        if cur.fetchone() is None:
            print(f"[Error: El correo electrónico no está registrado.]")
            return False
        cur.execute("UPDATE Usuarios SET nickname = %s WHERE correo_electronico = %s", 
                    (nickname, correo_electronico))
        conn.commit()
        cur.close()
        
        print("[Nickname actualizado correctamente.]")
        return True
        
    except mariadb.Error as e:
        print(f"Error al actualizar el nickname: {e}")
        return False


def obtener_contactos_usuario(conn, correo_electronico):
    try:
        cur = conn.cursor()
        cur.execute("USE LinuxLiveMessenger")
        cur.execute("""
            SELECT U.correo_electronico, U.nickname, C.fecha_agregado
            FROM Contactos C
            INNER JOIN Usuarios U ON U.correo_electronico = C.correo_electronico_contacto
            WHERE C.id_usuario = (SELECT id_usuario FROM Usuarios WHERE correo_electronico = %s);
        """, (correo_electronico,))
        resultados = cur.fetchall()
        cur.close()
        return resultados
    
    except mariadb.Error as e:
        print(Fore.LIGHTRED_EX + f"[Error al obtener contactos del usuario: {e}]")
        return None


def obtener_lema_usuario(conn, correo_electronico):
    try:
        cur = conn.cursor()
        cur.execute("USE LinuxLiveMessenger")
        cur.execute("""
            SELECT lema
            FROM Usuarios
            WHERE correo_electronico = %s
        """, (correo_electronico,))
        resultado = cur.fetchone()
        cur.close()

        if resultado is None:
            return None
        else:
            return resultado[0]

    except mariadb.Error as e:
        print(Fore.LIGHTRED_EX + f"[Error al obtener el lema del usuario: {e}]")
        return None


def agregar_contacto(conn, correo_electronico_usuario, correo_electronico_contacto):
    try:
        cur = conn.cursor()
        
        # Verificar si ambos correos electrónicos existen
        cur.execute("SELECT id_usuario FROM Usuarios WHERE correo_electronico = %s", (correo_electronico_usuario,))
        if cur.fetchone() is None:
            print(Fore.LIGHTRED_EX + f"[Error: El correo electrónico del usuario no está registrado.]")
            return False
        
        cur.execute("SELECT id_usuario FROM Usuarios WHERE correo_electronico = %s", (correo_electronico_contacto,))
        if cur.fetchone() is None:
            print(f"[Error: El correo electrónico del contacto no está registrado.]")
            return False
        
        # Verificar si ya son contactos
        cur.execute("""
            SELECT * FROM Contactos
            WHERE id_usuario = (SELECT id_usuario FROM Usuarios WHERE correo_electronico = %s)
            AND correo_electronico_contacto = %s
        """, (correo_electronico_usuario, correo_electronico_contacto))
        if cur.fetchone() is not None:
            print("[Error: Los usuarios ya son contactos.]")
            return False
        
        # Insertar el nuevo contacto en la tabla Contactos
        cur.execute("""
        INSERT INTO Contactos (id_usuario, correo_electronico_contacto, fecha_agregado) 
        VALUES ((SELECT id_usuario FROM Usuarios WHERE correo_electronico = %s), %s, %s)
        """, (correo_electronico_usuario, correo_electronico_contacto, datetime.datetime.now()))

        conn.commit()
        cur.close()
        
        print("[Contacto agregado correctamente.]")
        return True
        
    except mariadb.Error as e:
        print(f"Error al agregar el contacto: {e}")
        return False


def agregar_estado(conn, correo_electronico, texto_estado):
    try:
        cur = conn.cursor()
        cur.execute("USE LinuxLiveMessenger")
        cur.execute("""
            INSERT INTO Estados (id_usuario, texto_estado, fecha_hora)
            VALUES ((SELECT id_usuario FROM Usuarios WHERE correo_electronico = %s), %s, %s)
        """, (correo_electronico, texto_estado, datetime.datetime.now()))
        conn.commit()
        cur.close()
        
        print("[Estado actualizado correctamente.]")
        return True
        
    except mariadb.Error as e:
        print(f"Error al actualizar el estado: {e}")
        return False


def actualizar_lema(conn, correo_electronico, lema):
    try:
        cur = conn.cursor()
        cur.execute("SELECT id_usuario FROM Usuarios WHERE correo_electronico = %s", (correo_electronico,))
        if cur.fetchone() is None:
            print(f"[Error: El correo electrónico no está registrado.]")
            return False
        
        cur.execute("UPDATE Usuarios SET lema = %s WHERE correo_electronico = %s", 
                    (lema, correo_electronico))
        
        conn.commit()
        cur.close()
        
        print("[Lema actualizado correctamente.]")
        return True
        
    except mariadb.Error as e:
        print(f"Error al actualizar el lema: {e}")
        return False


def enviar_mensaje(conn, correo_electronico_usuario_envia, correo_electronico_usuario_recibe, texto_mensaje):
    try:
        cur = conn.cursor()

        cur.execute("SELECT id_usuario FROM Usuarios WHERE correo_electronico = %s", (correo_electronico_usuario_envia,))
        id_usuario_envia = cur.fetchone()
        if id_usuario_envia is None:
            print("El correo electrónico del remitente no existe.")
            return
        
        cur.execute("SELECT id_usuario FROM Usuarios WHERE correo_electronico = %s", (correo_electronico_usuario_recibe,))
        id_usuario_recibe = cur.fetchone()
        if id_usuario_recibe is None:
            print("El correo electrónico del destinatario no existe.")
            return
        
        cur.execute("INSERT INTO Mensajes (id_usuario_envia, id_usuario_recibe, texto_mensaje, fecha_hora) VALUES (%s, %s, %s, %s)", 
                    (id_usuario_envia[0], id_usuario_recibe[0], texto_mensaje, datetime.datetime.now()))
        
        conn.commit()
        cur.close()
        
        print("Mensaje enviado correctamente.")
        
    except mariadb.Error as e:
        print(f"Error al enviar el mensaje: {e}")


def obtener_estados_contactos(conn, correo_electronico):
    try:
        cur = conn.cursor()
        cur.execute("USE LinuxLiveMessenger")
        cur.execute("""
            SELECT U.correo_electronico, U.nickname, E.texto_estado, E.fecha_hora
            FROM Contactos C
            INNER JOIN Usuarios U ON U.correo_electronico = C.correo_electronico_contacto
            INNER JOIN Estados E ON E.id_usuario = U.id_usuario
            WHERE C.id_usuario = (SELECT id_usuario FROM Usuarios WHERE correo_electronico = %s);
        """, (correo_electronico,))
        resultados = cur.fetchall()
        cur.close()
        return resultados
    
    except mariadb.Error as e:
        print(Fore.LIGHTRED_EX + f"[Error al obtener estados de los contactos: {e}]")
        return None


def obtener_chat_usuarios(conn, correo_electronico_usuario1, correo_electronico_usuario2):
    try:
        cur = conn.cursor()
        cur.execute("SELECT id_usuario FROM Usuarios WHERE correo_electronico = %s", (correo_electronico_usuario1,))
        id_usuario1 = cur.fetchone()
        if id_usuario1 is None:
            print("El primer correo electrónico no corresponde a un usuario registrado.")
            return
        
        cur.execute("SELECT id_usuario FROM Usuarios WHERE correo_electronico = %s", (correo_electronico_usuario2,))
        id_usuario2 = cur.fetchone()
        if id_usuario2 is None:
            print("El segundo correo electrónico no corresponde a un usuario registrado.")
            return
        
        cur.execute("""
            SELECT m.texto_mensaje, m.fecha_hora, u1.correo_electronico as 'envia', u2.correo_electronico as 'recibe', m.id_mensaje
            FROM Mensajes m
            JOIN Usuarios u1 ON m.id_usuario_envia = u1.id_usuario
            JOIN Usuarios u2 ON m.id_usuario_recibe = u2.id_usuario
            WHERE (m.id_usuario_envia = %s AND m.id_usuario_recibe = %s)
               OR (m.id_usuario_envia = %s AND m.id_usuario_recibe = %s)
            ORDER BY m.fecha_hora ASC, m.id_mensaje ASC
        """, (id_usuario1[0], id_usuario2[0], id_usuario2[0], id_usuario1[0]))
        
        mensajes = cur.fetchall()

        cur.close()
        return mensajes
        
    except Exception as e:
        print(f"Error al obtener el chat entre los usuarios: {e}")
