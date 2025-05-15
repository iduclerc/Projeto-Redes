import socket
import time

def calcular_checksum(texto):
    return sum(ord(c) for c in texto)

def start_client(server_ip='localhost', port=5050):
    TIMEOUT_SEGUNDOS = 2

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, port))
    client_socket.settimeout(TIMEOUT_SEGUNDOS)

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
    total_pacotes = len(pacotes)
    client_socket.send(str(total_pacotes).encode())

    erro_idx = int(input(f"[Client] (Simular erro) Qual pacote deseja corromper? (1-{total_pacotes} ou 0 para nenhum): "))
    perda_idx = int(input(f"[Client] (Simular perda) Qual pacote deseja NÃO enviar? (1-{total_pacotes} ou 0 para nenhum): "))

    pacotes_enviados = {}  # {seq_num: pacote_formatado}
    tentativas = {}  # {seq_num: count}

    idx = 0
    while idx < total_pacotes:
        seq_num = idx + 1
        pacote = pacotes[idx]
        tentativas[seq_num] = tentativas.get(seq_num, 0) + 1

        if seq_num == perda_idx and tentativas[seq_num] == 1:
            print(f"[Client] (Simulando perda) Pacote #{seq_num} não enviado.")
            idx += 1
            continue

        if seq_num == erro_idx and tentativas[seq_num] == 1:
            checksum_original = calcular_checksum(pacote)
            pacote_enviado = "ERRO"
            checksum = checksum_original
            print(f"[Client] (Simulando erro) Pacote #{seq_num} ORIGINAL: '{pacote}' → ALTERADO para: '{pacote_enviado}'")
            print(f"[Client] Checksum enviado: {checksum} (calculado sobre original)")
        else:
            pacote_enviado = pacote
            checksum = calcular_checksum(pacote_enviado)

        pacote_formatado = f"SEQ:{seq_num}|{pacote_enviado}|CHK:{checksum}#"
        pacotes_enviados[seq_num] = pacote_formatado

        # ENVIO COM TIMEOUT E REENVIO AUTOMÁTICO
        while True:
            client_socket.send(pacote_formatado.encode())
            print(f"[Client] Pacote #{seq_num} enviado: {pacote_enviado} (CHK={checksum})")

            try:
                confirmacao = client_socket.recv(1024).decode()
                print(f"[Client] Confirmação recebida: {confirmacao}")
            except socket.timeout:
                print(f"[Client] Timeout esperando ACK do pacote {seq_num}, reenviando...")
                continue  # reenvia o mesmo pacote

            if confirmacao.startswith("ACK") and int(confirmacao.split()[1]) == seq_num:
                idx += 1
                break
            elif confirmacao.startswith("NACK"):
                print(f"[Client] NACK recebido para pacote {seq_num}, reenviando com conteúdo original.")
                pacote_enviado = pacotes[seq_num - 1]  # dado original
                checksum = calcular_checksum(pacote_enviado)
                pacote_formatado = f"SEQ:{seq_num}|{pacote_enviado}|CHK:{checksum}#"
                pacotes_enviados[seq_num] = pacote_formatado
                continue

        if modo_operacao == "individual":
            time.sleep(0.5)

    client_socket.close()

if __name__ == "__main__":
    start_client()
