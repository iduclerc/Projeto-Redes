import socket
import time
import threading

def calcular_checksum(texto):
    return sum(ord(c) for c in texto)

def start_client(server_ip='localhost', port=5050):
    TIMEOUT_SEGUNDOS = 2
    WINDOW_SIZE = 3

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

    pacotes_enviados = {}
    timers = {}
    acks_recebidos = set()
    lock = threading.Lock()

    def enviar_pacote(seq_num):
        if seq_num in acks_recebidos:
            return
        pacote = pacotes[seq_num - 1]
        if seq_num == erro_idx:
            pacote_enviado = "ERRO"
            checksum = calcular_checksum(pacote)
        else:
            pacote_enviado = pacote
            checksum = calcular_checksum(pacote_enviado)
        pacote_formatado = f"SEQ:{seq_num}|{pacote_enviado}|CHK:{checksum}#"
        if seq_num == perda_idx and seq_num not in pacotes_enviados:
            print(f"[Client] (Simulando perda) Pacote #{seq_num} não enviado.")
            return
        client_socket.send(pacote_formatado.encode())
        print(f"[Client] Pacote #{seq_num} enviado: {pacote_enviado} (CHK={checksum})")
        pacotes_enviados[seq_num] = pacote_formatado
        timers[seq_num] = time.time()

    def gerenciar_timeout():
        while len(acks_recebidos) < total_pacotes:
            time.sleep(0.1)
            with lock:
                agora = time.time()
                for seq_num in list(pacotes_enviados):
                    if seq_num not in acks_recebidos:
                        if agora - timers.get(seq_num, 0) > TIMEOUT_SEGUNDOS:
                            print(f"[Client] Timeout esperando ACK do pacote {seq_num}, reenviando...")
                            client_socket.send(pacotes_enviados[seq_num].encode())
                            timers[seq_num] = time.time()

    threading.Thread(target=gerenciar_timeout, daemon=True).start()

    base = 1
    next_seq = 1

    while len(acks_recebidos) < total_pacotes:
        with lock:
            while next_seq < base + WINDOW_SIZE and next_seq <= total_pacotes:
                if next_seq not in pacotes_enviados:
                    enviar_pacote(next_seq)
                next_seq += 1

        try:
            confirmacao = client_socket.recv(1024).decode()
            print(f"[Client] Confirmação recebida: {confirmacao}")
        except socket.timeout:
            continue

        if confirmacao.startswith("ACK"):
            try:
                ack_num = int(confirmacao.split()[1])
                with lock:
                    if ack_num not in acks_recebidos:
                        acks_recebidos.add(ack_num)
                        while base in acks_recebidos:
                            base += 1
            except:
                continue

        elif confirmacao.startswith("NACK"):
            try:
                nack_num = int(confirmacao.split()[1])
                with lock:
                    print(f"[Client] NACK recebido para pacote {nack_num}, reenviando com conteúdo original.")
                    pacote_original = pacotes[nack_num - 1]
                    checksum = calcular_checksum(pacote_original)
                    pacote_formatado = f"SEQ:{nack_num}|{pacote_original}|CHK:{checksum}#"
                    pacotes_enviados[nack_num] = pacote_formatado
                    client_socket.send(pacote_formatado.encode())
                    timers[nack_num] = time.time()
            except:
                continue

        if modo_operacao == "individual":
            time.sleep(0.5)

    client_socket.close()

if __name__ == "__main__":
    start_client()
