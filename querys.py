import mariadb
import sys
import datetime
from termcolor import colored
from colorama import init, Fore, Back, Style
import passlib.hash
import base64
import os


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
        actualizar_nickname(conn, correo_electronico, "Nuevo usuario")
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
        cur.execute("UPDATE Usuarios SET nickname = %s WHERE correo_electronico = %s", 
                    (nickname, correo_electronico))
        conn.commit()
        cur.close()
        
        respuesta_mariadb("Nickname actualizado", accion="actualizar nickname")
        return True
        
    except mariadb.Error as e:
        respuesta_mariadb(error=e, accion="actualizar nickname")
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
        respuesta_mariadb(error=e, accion="obtener contactos usuario")
        return None


def obtener_fotos_contactos(conn, correo_electronico):
    try:
        cur = conn.cursor()
        cur.execute("USE LinuxLiveMessenger")
        cur.execute("""
            SELECT U.correo_electronico, U.foto_perfil
            FROM Contactos C
            INNER JOIN Usuarios U ON U.correo_electronico = C.correo_electronico_contacto
            WHERE C.id_usuario = (SELECT id_usuario FROM Usuarios WHERE correo_electronico = %s);
        """, (correo_electronico,))
        resultados = cur.fetchall()
        cur.close()
        respuesta_mariadb("Fotos contactos obtenidas", accion="obtener fotos contactos")
        
        with open("ppic.png", "rb") as image_file:
            default_image_base64 = base64.b64encode(image_file.read()).decode("utf-8")
        
        fotos_contactos = []
        for contacto in resultados:
            correo_electronico_contacto, foto_perfil = contacto
            if foto_perfil is None:
                foto_perfil = default_image_base64
                fotos_contactos.append((correo_electronico_contacto, foto_perfil))
        
        return fotos_contactos

    except mariadb.Error as e:
        respuesta_mariadb(error=e, accion="obtener fotos contactos")
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
        respuesta_mariadb(error=e, accion="obtener lema usuario")
        return None


def agregar_contacto(conn, correo_electronico_usuario, correo_electronico_contacto):
    try:
        cur = conn.cursor()
        cur.execute("USE LinuxLiveMessenger")
        # Verificar si ya son contactos
        cur.execute("""
            SELECT * FROM Contactos
            WHERE id_usuario = (SELECT id_usuario FROM Usuarios WHERE correo_electronico = %s)
            AND correo_electronico_contacto = %s
        """, (correo_electronico_usuario, correo_electronico_contacto))
        if cur.fetchone() is not None:
            respuesta_mariadb(error="Los usuarios ya son contactos", accion="agregar contacto")
            return False
        
        # Insertar el nuevo contacto en la tabla Contactos
        cur.execute("""
        INSERT INTO Contactos (id_usuario, correo_electronico_contacto, fecha_agregado) 
        VALUES ((SELECT id_usuario FROM Usuarios WHERE correo_electronico = %s), %s, %s)
        """, (correo_electronico_usuario, correo_electronico_contacto, datetime.datetime.now()))

        conn.commit()
        cur.close()
        
        respuesta_mariadb("Contacto agregado correctamente", accion="agregar contacto")
        return True
        
    except mariadb.Error as e:
        respuesta_mariadb(error=e, accion="agregar contacto")
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
        
        respuesta_mariadb("Estado agregado correctamente", accion="agregar estado")
        return True
        
    except mariadb.Error as e:
        respuesta_mariadb(error=e, accion="agregar estado")
        return False


def actualizar_foto(conn, correo_electronico, imagenb64):
    try:
        cur = conn.cursor()
        cur.execute("USE LinuxLiveMessenger")
        
        cur.execute("""
            UPDATE Usuarios
            SET foto_perfil = %s
            WHERE correo_electronico = %s;
        """, (imagenb64, correo_electronico))
        conn.commit()
        cur.close()
        respuesta_mariadb("Foto actualizada exitosamente", accion="actualizar foto")
        return True

    except mariadb.Error as e:
        respuesta_mariadb(error=e, accion="actualizar foto")
        return False


def obtener_foto_usuario(conn, correo_electronico):
    try:
        cur = conn.cursor()
        cur.execute("USE LinuxLiveMessenger")
        cur.execute("""
            SELECT foto_perfil
            FROM Usuarios
            WHERE correo_electronico = %s;
        """, (correo_electronico,))
        resultado = cur.fetchone()
        cur.close()
        respuesta_mariadb("Foto de usuario obtenida", accion="obtener foto usuario")
        
        if resultado[0] is None:
            with open("ppic.png", "rb") as image_file:
                default_image_base64 = base64.b64encode(image_file.read()).decode("utf-8")
            return default_image_base64
        else:
            return resultado[0]

    except mariadb.Error as e:
        respuesta_mariadb(error=e, accion="obtener foto usuario")
        return None


def actualizar_lema(conn, correo_electronico, lema):
    try:
        cur = conn.cursor()
        cur.execute("UPDATE Usuarios SET lema = %s WHERE correo_electronico = %s", 
                    (lema, correo_electronico))
        
        conn.commit()
        cur.close()
        
        respuesta_mariadb("Lema actualizado correctamente", accion="actualizar lema")
        return True
        
    except mariadb.Error as e:
        respuesta_mariadb(error=e, accion="actualizar lema")
        return False


def enviar_mensaje(conn, correo_electronico_usuario_envia, correo_electronico_usuario_recibe, texto_mensaje):
    try:
        cur = conn.cursor()

        cur.execute("SELECT id_usuario FROM Usuarios WHERE correo_electronico = %s", (correo_electronico_usuario_envia,))
        id_usuario_envia = cur.fetchone()
        if id_usuario_envia is None:
            respuesta_mariadb(error="El correo electronico del remitente no existe", accion='enviar mensaje')
            return
        
        cur.execute("SELECT id_usuario FROM Usuarios WHERE correo_electronico = %s", (correo_electronico_usuario_recibe,))
        id_usuario_recibe = cur.fetchone()
        if id_usuario_recibe is None:
            respuesta_mariadb(error="El correo electrónico del destinatario no existe.", accion='enviar mensaje')
            return
        
        cur.execute("INSERT INTO Mensajes (id_usuario_envia, id_usuario_recibe, texto_mensaje, fecha_hora) VALUES (%s, %s, %s, %s)", 
                    (id_usuario_envia[0], id_usuario_recibe[0], texto_mensaje, datetime.datetime.now()))
        
        conn.commit()
        cur.close()
        
        respuesta_mariadb("Mensaje enviado correctamente", accion="enviar mensaje")
        
    except mariadb.Error as e:
        respuesta_mariadb(error=e, accion='enviar mensajes')


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

        # Convertir fechas de datetime a diccionarios
        resultados_formateados = []
        for resultado in resultados:
            fecha_hora = resultado[3]
            fecha_dict = {
                'year': fecha_hora.year,
                'month': fecha_hora.month,
                'day': fecha_hora.day,
                'hour': fecha_hora.hour,
                'minute': fecha_hora.minute,
                'second': fecha_hora.second
            }
            resultado_dict = {
                'email': resultado[0],
                'nickname': resultado[1],
                'texto_estado': resultado[2],
                'fecha_hora': fecha_dict
            }
            resultados_formateados.append(resultado_dict)
        
        cur.close()
        respuesta_mariadb("estados obtenidos correctamente", accion="obtener estados contactos")
        return resultados_formateados
    
    except mariadb.Error as e:
        respuesta_mariadb(error=e, accion="obtener estados contactos")
        return None


def obtener_chat_usuarios(conn, correo_electronico_usuario1, correo_electronico_usuario2):
    try:
        cur = conn.cursor()
        
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
        respuesta_mariadb("chat de los usuarios obtenido correctamente", accion="obtener chat usuarios")
        return mensajes
        
    except Exception as e:
        respuesta_mariadb(error=e, accion="obtener chat usuarios")
