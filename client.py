import ssl
import socket
import threading
import sys
import os
import time

SALA = "Sala por defecto"
USERNAME = ""
current_input = ""

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    banner_lines = r"""
 .----------------.  .----------------.  .----------------.  .----------------.  .----------------.  .----------------. 
| .--------------. || .--------------. || .--------------. || .--------------. || .--------------. || .--------------. |
| |  _________   | || |  _________   | || |  _______     | || | ____    ____ | || |    _______   | || |    ______    | |
| | |  _   _  |  | || | |_   ___  |  | || | |_   __ \    | || ||_   \  /   _|| || |   /  ___  |  | || |  .' ___  |   | |
| | |_/ | | \_|  | || |   | |_  \_|  | || |   | |__) |   | || |  |   \/   |  | || |  |  (__ \_|  | || | / .'   \_|   | |
| |     | |      | || |   |  _|  _   | || |   |  __ /    | || |  | |\  /| |  | || |   '.___`-.   | || | | |    ____  | |
| |    _| |_     | || |  _| |___/ |  | || |  _| |  \ \_  | || | _| |_\/_| |_ | || |  |`\____) |  | || | \ `.___]  _| | |
| |   |_____|    | || | |_________|  | || | |____| |___| | || ||_____||_____|| || |  |_______.'  | || |  `._____.'   | |
| |              | || |              | || |              | || |              | || |              | || |              | |
| '--------------' || '--------------' || '--------------' || '--------------' || '--------------' || '--------------' |
 '----------------'  '----------------'  '----------------'  '----------------'  '----------------'  '----------------' 
                                                                                                "Termsg" by nestore
"""
    for line in banner_lines.splitlines():
        print(line)
    print(f"Nombre de la sala: {SALA}")
    print("-" * (os.get_terminal_size().columns if os.name != "nt" else 80))

def redraw_screen():
    clear_screen()
    print_banner()
    print(f"[{USERNAME}]: ", end="", flush=True)

# ------------------- Validación de argumentos -------------------
if len(sys.argv) < 4:
    print("Uso: python client.py <IP_SERVIDOR> <cliente.crt> <cliente.key>")
    sys.exit(1)

SERVER_IP = sys.argv[1]
CERT_FILE = sys.argv[2]
KEY_FILE = sys.argv[3]

USERNAME = os.path.splitext(os.path.basename(CERT_FILE))[0]

# ------------------- Conexión TLS -------------------
context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile="ca.crt")
context.check_hostname = False
context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)

sock = socket.create_connection((SERVER_IP, 8443))
try:
    conn = context.wrap_socket(sock)
except ssl.SSLError as e:
    print(f"[!] Error TLS al conectar: {e}")
    sock.close()
    sys.exit(1)

# Enviar nombre al servidor
conn.send((USERNAME + "\n").encode())

# Mostrar banner y prompt inicial
redraw_screen()

# ------------------- Hilo para recibir mensajes -------------------
def receive_thread():
    global SALA
    while True:
        try:
            data = conn.recv(4096)
            if not data:
                print("\n[-] Desconectado del servidor")
                break
            text = data.decode().rstrip()

            # Mensaje de sala
            if text.startswith("[SALA]:"):
                SALA = text[len("[SALA]:"):].strip()
                redraw_screen()
                continue

            # Mover el prompt antes de imprimir mensaje
            print("\r" + " " * (len(USERNAME)+3 + len(current_input)) + "\r", end="")
            print(text)
            print(f"[{USERNAME}]: {current_input}", end="", flush=True)

        except:
            break

# ------------------- Hilo para input del usuario -------------------
def input_thread():
    global current_input
    while True:
        try:
            current_input = sys.stdin.readline().rstrip("\n")
            msg_lower = current_input.lower()
            if msg_lower == "/quit":
                conn.send(b"/quit\n")
                break
            elif msg_lower == "/clear":
                redraw_screen()
                continue
            elif msg_lower == "/usuarios":
                conn.send(b"/usuarios\n")
                continue
            else:
                conn.send((current_input + "\n").encode())
            current_input = ""  # reset input
            print(f"[{USERNAME}]: ", end="", flush=True)
        except:
            break

# ------------------- Iniciar hilos -------------------
threading.Thread(target=receive_thread, daemon=True).start()
threading.Thread(target=input_thread, daemon=True).start()

# Mantener vivo
while True:
    time.sleep(0.1)
