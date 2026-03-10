import socket
import os
import sys
import time
import subprocess

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
            
            # Robust reading to handle fragmentation
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

def test_server():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(base_dir, "server.py")
    server_proc = subprocess.Popen([sys.executable, server_path])
    time.sleep(1)
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            
            def send_and_recv(cmd):
                s.sendall((cmd + "\n").encode('utf-8'))
                return receive_full_message(s)
            
            print(f"ADD: {send_and_recv('ADD mouse 50')}")
            print(f"GET: {send_and_recv('GET mouse')}")
            print(f"LIST: {send_and_recv('LIST')}")
            print(f"COUNT: {send_and_recv('COUNT')}")
            print(f"UPDATE: {send_and_recv('UPDATE mouse 60')}")
            print(f"POP: {send_and_recv('POP mouse')}")
            print(f"CLEAR: {send_and_recv('CLEAR')}")
            print(f"QUIT: {send_and_recv('QUIT')}")
    finally:
        server_proc.terminate()

if __name__ == "__main__":
    test_server()
