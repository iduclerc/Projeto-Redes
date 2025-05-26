import socket
import time


def calcular_checksum(texto):
    return sum(ord(c) for c in texto)

def start_client(server_ip='localhost', port=5050):
    TIMEOUT_SEGUNDOS = 2
    janela = 1
    limite_exponencial = 32

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
    client_socket.send(str(len(pacotes)).encode())

    erro_idx = int(input(f"[Client] (Simular erro) Qual pacote deseja corromper? (1-{total_pacotes} ou 0 para nenhum): "))
    perda_idx = int(input(f"[Client] (Simular perda) Qual pacote deseja NÃO reenviar imediatamente? (1-{total_pacotes} ou 0 para nenhum): "))

    pacotes_enviados = {}
    tentativas = {}
    confirmados = set()
    reenviado_erro = False
    reenviar_perda_apos = False
    perda_esperando = False

    idx = 0
    while len(confirmados) < total_pacotes:
        if idx >= total_pacotes:
            reenviar_perda_apos = True
            idx = 0

        seq_num = idx + 1
        if seq_num in confirmados:
            idx += 1
            continue

        tentativas[seq_num] = tentativas.get(seq_num, 0) + 1
        print(f"[Janela] Tamanho atual da janela: {janela}")

        if tentativas[seq_num] > janela:
            print(f"[Janela] Pacote {seq_num} excede janela atual, aguardando ajuste.")
            time.sleep(TIMEOUT_SEGUNDOS)
            continue

        pacote = pacotes[seq_num - 1]
        flag_perda = (seq_num == perda_idx)
        flag_erro = (seq_num == erro_idx)

        if flag_perda:
            if not perda_esperando:
                perda_esperando = True
                client_socket.send(f"SEQ:{seq_num}|{pacote}|CHK:{calcular_checksum(pacote)}|FLAG:PERDA#".encode())
                print(f"[Client] Pacote #{seq_num} enviado (simulando perda com FLAG:PERDA)")
                idx += 1
                continue
            elif not reenviar_perda_apos:
                idx += 1
                continue

        if flag_erro and tentativas[seq_num] == 1:
            pacote_enviado = "ERRO"
            checksum = calcular_checksum(pacote)
            print(f"[Client] (Simulando erro) Pacote #{seq_num} ORIGINAL: '{pacote}' → ALTERADO para: '{pacote_enviado}'")
            print(f"[Client] Checksum enviado: {checksum} (calculado sobre original)")
        else:
            pacote_enviado = pacote
            checksum = calcular_checksum(pacote_enviado)
            if flag_erro:
                print(f"[Client] Reenvio do pacote #{seq_num} com conteúdo original (CHK={checksum})")

        pacote_formatado = f"SEQ:{seq_num}|{pacote_enviado}|CHK:{checksum}#"
        pacotes_enviados[seq_num] = pacote_formatado

        client_socket.send(pacote_formatado.encode())
        print(f"[Client] Pacote #{seq_num} enviado: {pacote_enviado} (CHK={checksum})")

        try:
            confirmacao = client_socket.recv(1024).decode().strip()
            print(f"[Client] Confirmação recebida: {confirmacao}")
        except socket.timeout:
            print(f"[Client] Timeout esperando ACK do pacote {seq_num}, diminuindo janela.")
            janela = max(1, janela // 2)
            print(f"[Janela] Reduzida para: {janela}")
            idx += 1
            continue

        partes = confirmacao.strip().split()
        if len(partes) == 2 and partes[0] == "ACK" and partes[1].isdigit() and int(partes[1]) == seq_num:
            confirmados.add(seq_num)
            if janela < limite_exponencial:
                janela = min(janela * 2, limite_exponencial)
            else:
                janela += 1
            print(f"[Janela] Aumentada para: {janela}")
            idx += 1
        elif len(partes) == 2 and partes[0] == "NACK" and partes[1].isdigit() and int(partes[1]) == seq_num:
            print(f"[Client] NACK recebido para pacote {seq_num}, reenviando com conteúdo original e diminuindo janela.")
            janela = max(1, janela // 2)
            print(f"[Janela] Reduzida para: {janela}")
            idx += 1
        else:
            print(f"[Client] Confirmação inválida ou fora de ordem recebida: {confirmacao}")
            idx += 1

        if modo_operacao == "individual":
            time.sleep(0.5)

    client_socket.close()

if __name__ == "__main__":
    start_client()
