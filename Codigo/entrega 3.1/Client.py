import socket
import time

def calcular_checksum(texto):
    return sum(ord(c) for c in texto)

def start_client(server_ip='localhost', port=5050):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, port))

    modo_operacao = input("[Client] Escolha o modo de operação (individual/lote): ").strip().lower()
    tamanho_max = int(input("[Client] Defina o tamanho máximo de caracteres por pacote: ").strip())

    handshake = f"{modo_operacao}|{tamanho_max}"
    client_socket.send(handshake.encode())
    print(f"[Client] Handshake enviado: {handshake}")
    resposta = client_socket.recv(1024).decode()
    print(f"[Client] Resposta do servidor: {resposta}")

    mensagem = input("[Client] Digite a mensagem para enviar ao servidor: ")
    print(f"[Client] Mensagem original: '{mensagem}'")

    pacotes = [mensagem[i:i+tamanho_max] for i in range(0, len(mensagem), tamanho_max)]
    client_socket.send(str(len(pacotes)).encode())

    erro_idx = int(input(f"[Client] (Simular erro) Qual pacote deseja corromper? (1-{len(pacotes)} ou 0 para nenhum): "))
    perda_idx = int(input(f"[Client] (Simular perda) Qual pacote deseja NÃO enviar? (1-{len(pacotes)} ou 0 para nenhum): "))

    for idx, pacote in enumerate(pacotes):
        seq_num = idx + 1

        if seq_num == perda_idx:
            print(f"[Client] (Simulando perda) Pacote #{seq_num} não enviado.")
            continue

        if seq_num == erro_idx:
            checksum_original = calcular_checksum(pacote)  
            pacote_enviado = "ERRO"                        
            checksum = checksum_original                   
            print(f"[Client] (Simulando erro) Pacote #{seq_num} alterado para: '{pacote_enviado}' (CHK calculado sobre original '{pacote}': {checksum_original})")


        else:
            pacote_enviado = pacote
            checksum = calcular_checksum(pacote_enviado)

        pacote_formatado = f"SEQ:{seq_num}|{pacote_enviado}|CHK:{checksum}#"
        client_socket.send(pacote_formatado.encode())
        print(f"[Client] Pacote #{seq_num} enviado: {pacote_enviado} (CHK={checksum})")

        confirmacao = client_socket.recv(1024).decode()
        print(f"[Client] Confirmação recebida: {confirmacao}")

        if modo_operacao == "individual":
            time.sleep(0.5)

    client_socket.close()

if __name__ == "__main__":
    start_client()
