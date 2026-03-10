import socket
import threading

HOST = "127.0.0.1"
PORT = 12345
BUFFER_SIZE = 1024

class State:
    def __init__(self):
        self.dic = {}
        self.lock = threading.Lock()

    def add(self, key, value):
        with self.lock:
            self.dic[key] = value
            return "OK - record add"

    def get(self, key):
        with self.lock:
            val = self.dic.get(key)
            return f"DATA {val}" if val else "ERROR invalid key"

    def remove(self, key):
        with self.lock:
            if key in self.dic:
                del self.dic[key]
                return "OK value deleted"
            return "ERROR invalid key"

    def list_all(self):
        with self.lock:
            items = [f"{k}={v}" for k, v in self.dic.items()]
            return f"DATA|{','.join(items)}"

    def count(self):
        with self.lock:
            return f"DATA {len(self.dic)}"

    def clear(self):
        with self.lock:
            self.dic.clear()
            return "all data deleted"

    def update(self, key, value):
        with self.lock:
            if key in self.dic:
                self.dic[key] = value
                return "Data updated"
            return "ERROR invalid key"

    def pop(self, key):
        with self.lock:
            if key in self.dic:
                val = self.dic.pop(key)
                return f"Data {val}"
            return "ERROR invalid key"

state = State()

def process_command(command):
    parts = command.split()
    if not parts: return "ERROR empty command"
    cmd = parts[0].upper()
    
    if cmd == "ADD" and len(parts) >= 3:
        return state.add(parts[1], " ".join(parts[2:]))
    elif cmd == "GET" and len(parts) >= 2:
        return state.get(parts[1])
    elif cmd == "REMOVE" and len(parts) >= 2:
        return state.remove(parts[1])
    elif cmd == "LIST":
        return state.list_all()
    elif cmd == "COUNT":
        return state.count()
    elif cmd == "CLEAR":
        return state.clear()
    elif cmd == "UPDATE" and len(parts) >= 3:
        return state.update(parts[1], " ".join(parts[2:]))
    elif cmd == "POP" and len(parts) >= 2:
        return state.pop(parts[1])
    elif cmd == "QUIT":
        return "QUIT"
    
    return "ERROR unknown command or invalid params"

def handle_client(client_socket):
    with client_socket:
        while True:
            try:
                data = client_socket.recv(BUFFER_SIZE)
                if not data: break
                
                command = data.decode('utf-8').strip()
                response = process_command(command)
                
                if response == "QUIT":
                    msg = "Closing connection"
                    client_socket.sendall(f"{len(msg)} {msg}\n".encode('utf-8'))
                    break
                
                response_data = f"{len(response)} {response}\n".encode('utf-8')
                client_socket.sendall(response_data)
            except Exception:
                break

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        while True:
            conn, addr = server_socket.accept()
            threading.Thread(target=handle_client, args=(conn,), daemon=True).start()

if __name__ == "__main__":
    start_server()
