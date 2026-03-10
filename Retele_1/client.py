import socket

HOST = "127.0.0.1"
PORT = 12345
BUFFER_SIZE = 1024

def receive_full_message(sock):
    try:
        data = sock.recv(BUFFER_SIZE)
        if not data: return None
        
        string_data = data.decode('utf-8').strip()
        first_space = string_data.find(' ')
        if first_space == -1: return string_data
        
        try:
            message_length = int(string_data[:first_space])
            full_data = string_data[first_space + 1:]
            
            remaining = message_length - len(full_data.encode('utf-8'))
            while remaining > 0:
                data = sock.recv(min(remaining, BUFFER_SIZE))
                if not data: break
                full_data += data.decode('utf-8')
                remaining -= len(data)
            
            return full_data
        except ValueError:
            return string_data
    except Exception as e:
        return f"Error: {e}"

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
            print(f"Conectat la server pe {HOST}:{PORT}")
            print("Introdu comenzi (ADD, GET, REMOVE, LIST, COUNT, CLEAR, UPDATE, POP, QUIT):")
            
            while True:
                command = input("client> ").strip()
                if not command: continue
                
                s.sendall((command + "\n").encode('utf-8'))
                
                response = receive_full_message(s)
                print(f"Server response: {response}")
                
                if command.upper() == "QUIT" or response == "Closing connection":
                    break
        except ConnectionRefusedError:
            print("Eroare: Serverul nu este pornit! Rulează 'py server.py' mai întâi.")

if __name__ == "__main__":
    main()
