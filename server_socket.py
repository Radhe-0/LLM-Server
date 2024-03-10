import asyncio
import random
import string
import json
import websockets
from websockets.server import serve
from pprint import pprint
from termcolor import colored
from colorama import init, Fore, Back, Style
import querys
import base64
import os

PORT = 8765 # puerto del websocket
HOST = "localhost"
conexiones_activas = {} # email: websocket


async def obtener_nickname_usuario(websocket, email):
    conn = querys.conectar_mariadb()
    nickname = querys.obtener_nickname_usuario(conn, email)

    try:
        mensaje = {'tipo': 'obtener_nickname', 'data': nickname}
        await websocket.send(json.dumps(mensaje))
        await texto_respuesta(mensaje)
    except websockets.exceptions.ConnectionClosedOK:
        print("La conexión se cerró antes de enviar el mensaje.")


async def obtener_estados_contactos(websocket, email):
    conn = querys.conectar_mariadb()
    estados_data = querys.obtener_estados_contactos(conn, email)

    try:
        mensaje = {'tipo': 'obtener_estados', 'data': estados_data}
        await websocket.send(json.dumps(mensaje))
        await texto_respuesta(mensaje)
    except websockets.exceptions.ConnectionClosedOK:
        print("La conexión se cerró antes de enviar el mensaje.")


async def actualizar_foto(websocket, email, imagenb64):
    conn = querys.conectar_mariadb()
    querys.actualizar_foto(conn, email, imagenb64)

    try:
        mensaje = {'tipo': 'actualizar_foto', 'data': {'imagenb64': imagenb64, 'email': email}} # la imagen se convertirá en binario
        await websocket.send(json.dumps(mensaje))
        await texto_respuesta(mensaje)
    except websockets.exceptions.ConnectionClosedOK:
        print("La conexión se cerró antes de enviar el mensaje.")


async def actualizar_nickname_usuario(websocket, email, nuevo_nickname):
    conn = querys.conectar_mariadb()
    exito = querys.actualizar_nickname(conn, email, nuevo_nickname)

    if exito != True:
        print("Hubo un problema con el cambio de nickname")
        return

    try:
        mensaje = {'tipo': 'actualizar_nickname', 'data': nuevo_nickname}
        await websocket.send(json.dumps(mensaje))
        await texto_respuesta(mensaje)
    except websockets.exceptions.ConnectionClosedOK:
        print("La conexión se cerró antes de enviar el mensaje.")


async def agregar_contacto(websocket, email, email_contacto):
    conn = querys.conectar_mariadb()
    exito = querys.agregar_contacto(conn, email, email_contacto)

    if exito != True:
        print("Hubo un problema agregando el contacto")
        return

    try:
        mensaje = {'tipo': 'agregar_contacto', 'data': {"email": email, "email_contacto": email_contacto}}
        await websocket.send(json.dumps(mensaje))
        await texto_respuesta(mensaje)
    except websockets.exceptions.ConnectionClosedOK:
        print("La conexión se cerró antes de enviar el mensaje.")

##################################################################################

async def handler(websocket):
    async for message_0 in websocket:
        mensaje = limpiar_str(str(message_0))
        solicitud = eval(mensaje) # str a dict
        await texto_solicitud(solicitud)

        
        if solicitud['accion'] == 'obtener_nickname':
            await obtener_nickname_usuario(websocket, solicitud['data']['email'])

        elif solicitud['accion'] == 'obtener_estados':
            await obtener_estados_contactos(websocket, solicitud['data']['email'])

        elif solicitud['accion'] == 'actualizar_foto':
            await actualizar_foto(websocket, solicitud['data']['email'], solicitud['data']['imagenb64']) 

        elif solicitud['accion'] == 'agregar_contacto':
            await agregar_contacto(websocket, solicitud['data']['email'], solicitud['data']['email_contacto'])
            
##################################################################################
     
async def texto_solicitud(solicitud):
    if 'imagenb64' in solicitud['data']:
        print("-"*64)
        print(Fore.BLUE + Style.BRIGHT+ "[Solicitud recibida]:\t" + Fore.LIGHTMAGENTA_EX + solicitud["accion"] + Fore.RESET + Style.RESET_ALL)
        print("imagenb64 recibida")

    else:
        print("-"*64)
        print(Fore.BLUE + Style.BRIGHT+ "[Solicitud recibida]:\t" + Fore.LIGHTMAGENTA_EX + solicitud["accion"] + Fore.RESET + Style.RESET_ALL)
        pprint(solicitud)

async def texto_respuesta(respuesta):
    if 'imagenb64' in respuesta['data'] or 'obtener_contactos' == respuesta['tipo']:
        print("-"*64)
        print(Fore.LIGHTGREEN_EX + Style.BRIGHT+ "[Respuesta enviada]:\t" + Fore.LIGHTMAGENTA_EX + respuesta["tipo"] + Fore.RESET + Style.RESET_ALL)
        pprint('imagenesb64 enviadas')
    else:
        print("-"*64)
        print(Fore.LIGHTGREEN_EX + Style.BRIGHT+ "[Respuesta enviada]:\t" + Fore.LIGHTMAGENTA_EX + respuesta["tipo"] + Fore.RESET + Style.RESET_ALL)
        pprint(respuesta)


def limpiar_str(texto_crudo: str):
    i_1 = texto_crudo.find("{")
    i_2 = texto_crudo.rfind("}")
    mensaje = texto_crudo[i_1 : i_2 +1]
    return mensaje

def generar_id():
    caracteres = string.ascii_uppercase + string.digits
    id = ''.join(random.choice(caracteres) for _ in range(4))
    return id




async def main():
    async with serve(handler, HOST, PORT,max_size=None):

        print(Fore.CYAN + Style.BRIGHT + "╔══════════════════════════════════════════════════════════╗")
        print(Fore.CYAN + "║\t\t     " + Fore.LIGHTRED_EX +  "[Servidor iniciado]" + Fore.CYAN + "\t\t   ║")
        print(Fore.CYAN + "║" + Fore.LIGHTCYAN_EX + Style.BRIGHT + "Host: " + Fore.WHITE + f"{HOST}\t\t\t\t\t   " + Fore.CYAN + "║")
        print(Fore.CYAN + "║" + Fore.LIGHTCYAN_EX + Style.BRIGHT + "Puerto: " + Fore.WHITE + f"{PORT}\t\t\t\t\t\t   " + Fore.CYAN + "║")
        print(Fore.CYAN + "╚══════════════════════════════════════════════════════════╝", Fore.RESET, Style.RESET_ALL)

        await asyncio.get_running_loop().create_future()


try:
    asyncio.run(main())
except KeyboardInterrupt:
        print(Fore.RED + Style.BRIGHT + "[Servidor detenido]" + Style.RESET_ALL)

