import socket

def start_server(host='localhost', port=5050):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)

    print(f"[Server] Aguardando conexão em {host}:{port}...")
    conn, addr = server_socket.accept()
    print(f"[Server] Conectado por {addr}")

    handshake_data = conn.recv(1024).decode()# recebe o handshake(processo cliente servidor).
    print(f"[Server] Handshake recebido: {handshake_data}")

    modo_operacao, tamanho_max = handshake_data.split("|")#Faz o processamento das informações .
    print(f"[Server] Modo de operação: {modo_operacao}")
    print(f"[Server] Tamanho máximo permitido: {tamanho_max}")

    conn.send("Handshake OK".encode())#confirma o processamento

    conn.close()
    server_socket.close()

if __name__ == "__main__":
    start_server()
