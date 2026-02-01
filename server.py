import socket
import ssl
import threading
import sys

if len(sys.argv) < 2:
    print("Uso: python3 server.py <nombre_de_sala>")
    sys.exit(1)

SALA = sys.argv[1]
HOST = '0.0.0.0'
PORT = 8443

clients = []  # [(conn, username)]
lock = threading.Lock()
running = True
server_socket = None

def safe_send(conn, msg):
    try:
        conn.send(msg.encode())
    except:
        pass

def broadcast(msg, sender_conn=None):
    with lock:
        for conn, _ in clients[:]:
            if conn != sender_conn:
                safe_send(conn, msg)

def send_users_list():
    with lock:
        user_list = ", ".join(f"{u}@{c.getpeername()[0]}" for c, u in clients)
        for conn, _ in clients:
            safe_send(conn, f"[USERS]: {user_list}\n")

def handle_client(conn):
    username = None
    try:
        # Recibir nombre de usuario
        data = conn.recv(1024)
        if not data:
            return
        username = data.decode().strip()

        # Agregar a la lista de clientes
        with lock:
            clients.append((conn, username))

        print(f"[+] {username} se ha unido", flush=True)

        # Enviar nombre de la sala al cliente para actualizar banner
        safe_send(conn, f"[SALA]:{SALA}\n")

        broadcast(f"[+] {username} se ha unido\n", conn)
        # send_users_list()  # Eliminado para no enviar lista automáticamente

        buffer = ""
        while running:
            try:
                data = conn.recv(1024)
                if not data:
                    break
                buffer += data.decode()
            except ssl.SSLError:
                break

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()
                if line == "/quit":
                    return
                elif line == "/usuarios":
                    with lock:
                        users = ", ".join(u for _, u in clients)
                    safe_send(conn, f"[Usuarios]: {users}\n")
                else:
                    msg = f"[{username}]: {line}\n"
                    print(msg.strip(), flush=True)
                    broadcast(msg, conn)

    finally:
        if username:
            with lock:
                clients[:] = [(c, u) for c, u in clients if c != conn]
            broadcast(f"[-] {username} se ha desconectado\n")  # Notificar desconexión
            # send_users_list()  # seguimos sin enviar lista automática
        try:
            conn.close()
        except:
            pass

def server_commands():
    global running
    while running:
        cmd = input().strip()
        if cmd.startswith("/kick "):
            target = cmd.split(" ", 1)[1]
            with lock:
                for conn, user in clients:
                    if user == target:
                        print(f"[!] Kickeando a {user}", flush=True)
                        safe_send(conn, "[!] Has sido expulsado por el servidor\n")
                        try:
                            conn.close()
                        except:
                            pass
                        clients[:] = [(c, u) for c, u in clients if u != user]
                        # send_users_list()  # Opcional si quieres que la lista se actualice al kick
                        break
                else:
                    print("[!] Usuario no encontrado", flush=True)

        elif cmd == "/shutdown":
            print("[!] Cerrando servidor...", flush=True)
            running = False
            broadcast("[!] El servidor se está cerrando\n")
            with lock:
                for conn, _ in clients:
                    try:
                        conn.close()
                    except:
                        pass
                clients.clear()
            try:
                server_socket.close()
            except:
                pass
            print("✔ Servidor apagado", flush=True)
            sys.exit(0)

def main():
    global server_socket
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_cert_chain("server.crt", "server.key")
    context.load_verify_locations("ca.crt")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)

    print(f"🔐 Termsg activo en {HOST}:{PORT} - Sala: {SALA}", flush=True)

    threading.Thread(target=server_commands, daemon=True).start()

    while running:
        try:
            client, addr = server_socket.accept()
            conn = context.wrap_socket(client, server_side=True)
            threading.Thread(target=handle_client, args=(conn,), daemon=True).start()
        except Exception as e:
            if running:
                print(f"[!] Error aceptando cliente: {e}", flush=True)
            break

if __name__ == "__main__":
    main()
