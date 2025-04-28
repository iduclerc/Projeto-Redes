import socket

def start_server(host='localhost', port=5050):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)

    print(f"[Server] Aguardando conexão em {host}:{port}...")
    conn, addr = server_socket.accept()
    print(f"[Server] Conectado por {addr}")

    handshake_data = conn.recv(1024).decode()
    modo_operacao, tamanho_max = handshake_data.split("|")
    print(f"[Server] Handshake recebido: {handshake_data}")
    print(f"[Server] Modo de operação: {modo_operacao}")
    print(f"[Server] Tamanho máximo permitido: {tamanho_max}")

    conn.send("Handshake OK".encode())

    num_pacotes = int(conn.recv(1024).decode())
    print(f"[Server] Número de pacotes esperados: {num_pacotes}")

    mensagem_reconstruida = ""
    buffer = ""
    pacotes_recebidos = 0

    conn.settimeout(2)  
    
    try:
        while pacotes_recebidos < num_pacotes:
            try:
                dados = conn.recv(1024).decode()
                if not dados:
                    continue
                buffer += dados

                while "#" in buffer:
                    pacote, buffer = buffer.split("#", 1)
                    print(f"[Server] Pacote recebido: {pacote}")
                    mensagem_reconstruida += pacote
                    pacotes_recebidos += 1

                    conn.send("ACK".encode())

                    if pacotes_recebidos >= num_pacotes:
                        break
            except socket.timeout:
                continue  # Se passar 2s sem dados, tenta novamente
    except Exception as e:
        print(f"[Server] Erro durante a recepção: {e}")

    print(f"[Server] Mensagem completa recebida: {mensagem_reconstruida}")
    conn.close()
    server_socket.close()

if __name__ == "__main__":
    start_server()
