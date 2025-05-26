import socket

def calcular_checksum(texto):
    return sum(ord(c) for c in texto)

def start_server(host='localhost', port=5050):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)

    print("[Server] Aguardando conexão em localhost:5050...")
    conn, addr = server_socket.accept()
    print(f"[Server] Conectado por {addr}")

    handshake_data = conn.recv(1024).decode()
    modo_operacao, tamanho_max = handshake_data.split("|")
    print(f"[Server] Handshake recebido: {handshake_data}")
    conn.send("Handshake OK".encode())

    num_pacotes = int(conn.recv(1024).decode())
    print(f"[Server] Número de pacotes esperados: {num_pacotes}")

    mensagem_reconstruida = [None] * num_pacotes
    pacotes_recebidos = set()
    buffer = ""

    while len(pacotes_recebidos) < num_pacotes:
        dados = conn.recv(1024).decode()
        buffer += dados

        while "#" in buffer:
            pacote_raw, buffer = buffer.split("#", 1)

            try:
                partes = pacote_raw.split("|")
                seq = int(partes[0].split(":")[1])
                conteudo = partes[1]
                chk = int(partes[2].split(":")[1])
                flag = partes[3].split(":")[1] if len(partes) > 3 else "OK"
            except:
                print(f"[Server] Erro no formato do pacote: {pacote_raw}")
                continue

            print(f"[Server] Pacote SEQ {seq} recebido: '{conteudo}' (CHK={chk})")

            if flag == "PERDA":
                print(f"[Server] Pacote SEQ {seq} marcado com PERDA. Ignorando confirmação.")
                continue

            checksum_calc = calcular_checksum(conteudo)
            if checksum_calc != chk:
                print(f"[Server] Erro de integridade no pacote SEQ {seq}: esperado {chk}, recebido {checksum_calc}")
                conn.send(f"NACK {seq}".encode())
                continue

            if seq not in pacotes_recebidos:
                mensagem_reconstruida[seq - 1] = conteudo
                pacotes_recebidos.add(seq)
                print(f"[Server] Pacote SEQ {seq} armazenado com sucesso.")

            conn.send(f"ACK {seq}".encode())

    mensagem_final = ''.join(mensagem_reconstruida)
    print(f"[Server] Mensagem final reconstruída: {mensagem_final}")

    conn.close()
    server_socket.close()

if __name__ == "__main__":
    start_server()
