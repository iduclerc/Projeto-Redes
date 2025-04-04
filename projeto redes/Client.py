import socket

def start_client(server_ip='localhost', port=5050):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, port))

    # Handshake
    modo_operacao = input("[Client] Escolha o modo de operação (individual/lote): ").strip().lower()
    tamanho_max = input("[Client] Defina o tamanho máximo da mensagem: ").strip()
    
    handshake = f"{modo_operacao}|{tamanho_max}"

    client_socket.send(handshake.encode())

    print(f"[Client] Handshake enviado: {handshake}")

    resposta = client_socket.recv(1024).decode()# para receber a confirmação da ação .
    print(f"[Client] Resposta do servidor: {resposta}")

    # Mensagem do usuário
    mensagem = input("[Client] Digite a mensagem para enviar ao servidor: ")

    # Dividindo em pacotes de 3 caracteres
    pacotes = [mensagem[i:i+3] for i in range(0, len(mensagem), 3)]
    client_socket.send(str(len(pacotes)).encode())  # Envia quantidade de pacotes

    # Enviando os pacotes
    for pacote in pacotes:
        pacote_com_delim = pacote + "#"  # adiciona delimitador
        client_socket.send(pacote_com_delim.encode())
        print(f"[Client] Pacote enviado: {pacote}")

        if modo_operacao == "individual":
            confirmacao = client_socket.recv(1024).decode()
            print(f"[Client] Confirmação recebida do servidor: {confirmacao}")

    client_socket.close()

if __name__ == "__main__":
    start_client() 