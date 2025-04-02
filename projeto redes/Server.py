import socket

def start_server(host='localhost', port=5050):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)

    print(f"[Server] Aguardando conexão em {host}:{port}...")
    conn, addr = server_socket.accept()
    
    print(f"[Server] Conectado por {addr}")

    # recebe o handshake(processo cliente servidor).
    handshake_data = conn.recv(1024).decode()
    print(f"[Server] Handshake recebido: {handshake_data}")
    
    modo_operacao, tamanho_max = handshake_data.split("|")#Faz o processamento das informações .

    print(f"[Server] Modo de operação: {modo_operacao}")
    print(f"[Server] Tamanho máximo permitido: {tamanho_max}")

    conn.send("Handshake OK".encode())#confirma o processamento

    # Recebe número de pacotes
    num_pacotes = int(conn.recv(1024).decode())
    print(f"[Server] Número de pacotes esperados: {num_pacotes}")

    mensagem_reconstruida = ""
    buffer = ""
    pacotes_recebidos = 0

    while pacotes_recebidos < num_pacotes:
        dados = conn.recv(1024).decode()
        buffer += dados

        while "#" in buffer:
            pacote, buffer = buffer.split("#", 1)
            print(f"[Servidor] Pacote recebido: {pacote}")
            mensagem_reconstruida += pacote
            pacotes_recebidos += 1

            if pacotes_recebidos >= num_pacotes:
                break

    print(f"[Server] Mensagem completa recebida: {mensagem_reconstruida}")

    conn.close()
    server_socket.close()

if __name__ == "__main__":
    start_server()
