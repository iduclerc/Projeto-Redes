import socket

def start_client(server_ip='localhost', port=5050):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, port))

    modo_operacao = "lote" 
    tamanho_max = "100"     

    handshake = f"{modo_operacao}|{tamanho_max}"
    client_socket.send(handshake.encode())
    print(f"[Cliente] Handshake enviado: {handshake}")

    resposta = client_socket.recv(1024).decode()# para receber a confirmação da ação .
    print(f"[Cliente] Resposta do servidor: {resposta}")

    client_socket.close()

if __name__ == "__main__":
    start_client()
