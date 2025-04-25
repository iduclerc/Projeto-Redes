import socket
import time

def start_client(server_ip='localhost', port=5050):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, port))

    # Handshake
    modo_operacao = input("[Client] Escolha o modo de operação (individual/lote): ").strip().lower()
    tamanho_max = input("[Client] Defina o tamanho máximo da mensagem: ").strip()
    
    handshake = f"{modo_operacao}|{tamanho_max}"
    client_socket.send(handshake.encode())
    print(f"[Client] Handshake enviado: {handshake}")

    resposta = client_socket.recv(1024).decode()
    print(f"[Client] Resposta do servidor: {resposta}")

    # Entrada da mensagem
    mensagem = input("[Client] Digite a mensagem para enviar ao servidor: ")
    mensagem = mensagem[:int(tamanho_max)]
    print(f"[Client] Mensagem ajustada para envio: '{mensagem}'")

    # Divisão dos pacotes
    if modo_operacao == "lote":
        pacotes = [mensagem[i:i+3] for i in range(0, len(mensagem), 3)]
    else:  # modo individual
        pacotes = list(mensagem)  # envia um caractere por vez

    client_socket.send(str(len(pacotes)).encode())  # Envia a quantidade de pacotes

    # Envio dos pacotes
    for idx, pacote in enumerate(pacotes):
        pacote_com_delim = pacote + "#"
        client_socket.send(pacote_com_delim.encode())
        print(f"[Client] Pacote #{idx+1} enviado: {pacote}")

        # Aguarda confirmação do servidor
        confirmacao = client_socket.recv(1024).decode()
        print(f"[Client] Metadado de confirmação → Pacote #{idx+1}, Conteúdo: '{pacote}', Tipo: {confirmacao}")

        # Delay entre pacotes apenas no modo individual
        if modo_operacao == "individual":
            time.sleep(0.5)

    client_socket.close()

if __name__ == "__main__":
    start_client()
