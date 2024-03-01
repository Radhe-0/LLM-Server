import asyncio
import random
import string
import json
import websockets
from websockets.server import serve
from pprint import pprint
from termcolor import colored
from colorama import init, Fore, Back, Style
from querys import nuevo_usuario, login, actualizar_lema, actualizar_nickname, agregar_contacto, obtener_chat_usuarios, conectar_mariadb
from querys import obtener_contactos_usuario, obtener_estados_contactos, obtener_lema_usuario, enviar_mensaje, agregar_estado


PORT = 8765 # puerto del websocket
HOST = "localhost"


async def nuevo_usuario(websocket, data):
    try:
        mensaje = {'tipo':'nuevo_usuario'}
    except websockets.exceptions.ConnectionClosedOK:
        print("La conexión se cerró antes de enviar el mensaje.")


async def obtener_contactos(websocket, data):
    try:
        mensaje = {'tipo': 'obtener_contactos', 'data': "CONTACTOS"}
        await websocket.send(json.dumps(mensaje))
        await texto_respuesta(mensaje)

    except websockets.exceptions.ConnectionClosedOK:
        print("La conexión se cerró antes de enviar el mensaje.")


async def obtener_contactos(websocket, data):
    try:
        mensaje = {'tipo': 'obtener_contactos', 'data': salas[sala_id]}
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

        if solicitud['accion'] == 'obtener_contactos':
            await obtener_contactos(websocket, solicitud['data'])
        
        elif solicitud['accion'] == 'obtener_estados':
            await obtener
            
##################################################################################
     
async def texto_solicitud(solicitud):
    print("-"*64)
    print(Fore.BLUE + Style.BRIGHT+ "[Solicitud recibida]:\t" + Fore.LIGHTMAGENTA_EX + solicitud["accion"] + Fore.RESET)
    pprint(solicitud)

async def texto_respuesta(respuesta):
    print("-"*64)
    print(Fore.LIGHTGREEN_EX + Style.BRIGHT+ "[Respuesta enviada]:\t" + Fore.LIGHTMAGENTA_EX + respuesta["tipo"] + Fore.RESET)
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
    async with serve(handler, HOST, PORT):

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