import socket

def start_client(server_ip='localhost', port=5050):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, port))

    modo_operacao = input("[Client] Escolha o modo de operação (individual/lote): ").strip().lower()
    tamanho_max = input("[Client] Defina o tamanho máximo da mensagem: ").strip()

    handshake = f"{modo_operacao}|{tamanho_max}"

    client_socket.send(handshake.encode())
    print(f"[Client] Handshake enviado: {handshake}")

    resposta = client_socket.recv(1024).decode()# para receber a confirmação da ação .
    print(f"[Client] Resposta do servidor: {resposta}")

    client_socket.close()

if __name__ == "__main__":
    start_client()
