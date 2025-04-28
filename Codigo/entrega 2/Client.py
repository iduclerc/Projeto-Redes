import socket
import time

def start_client(server_ip='localhost', port=5050):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, port))

    # Handshake
    modo_operacao = input("[Client] Escolha o modo de operação (individual/lote): ").strip().lower()
    tamanho_max = int(input("[Client] Defina o tamanho máximo de caracteres por pacote: ").strip())

    handshake = f"{modo_operacao}|{tamanho_max}"
    client_socket.send(handshake.encode())
    print(f"[Client] Handshake enviado: {handshake}")

    resposta = client_socket.recv(1024).decode()
    print(f"[Client] Resposta do servidor: {resposta}")

    # Entrada da mensagem
    mensagem = input("[Client] Digite a mensagem para enviar ao servidor: ")
    print(f"[Client] Mensagem ajustada para envio: '{mensagem}'")

    # Divisão dos pacotes (modo não muda a divisão)
    pacotes = [mensagem[i:i+tamanho_max] for i in range(0, len(mensagem), tamanho_max)]

    client_socket.send(str(len(pacotes)).encode())  # Envia a quantidade de pacotes

    # Envio dos pacotes
    for idx, pacote in enumerate(pacotes):
        pacote_com_delim = pacote + "#"
        client_socket.send(pacote_com_delim.encode())
        print(f"[Client] Pacote #{idx+1} enviado: {pacote}")

        # Aguarda confirmação do servidor
        confirmacao = client_socket.recv(1024).decode()
        print(f"[Client] Metadado de confirmação → Pacote #{idx+1}, Conteúdo: '{pacote}', Tipo: {confirmacao}")

        # Delay apenas no modo individual
        if modo_operacao == "individual":
            time.sleep(0.5)

    client_socket.close()

if __name__ == "__main__":
    start_client()
