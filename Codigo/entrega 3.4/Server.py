import socket

def calcular_checksum(texto):
    return sum(ord(c) for c in texto)

def start_server(host='localhost', port=5050):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)

    print(f"[Server] Aguardando conexão em {host}:{port}...")
    conn, addr = server_socket.accept()
    print(f"[Server] Conectado por {addr}")

    handshake_data = conn.recv(1024).decode()
    modo_operacao, tamanho_max = handshake_data.split("|")
    print(f"[Server] Handshake recebido: {handshake_data}")
    conn.send("Handshake OK".encode())

    num_pacotes = int(conn.recv(1024).decode())
    print(f"[Server] Número de pacotes esperados: {num_pacotes}")

    mensagem_reconstruida = [None] * num_pacotes
    buffer = ""
    recebidos = set()

    while len(recebidos) < num_pacotes:
        dados = conn.recv(1024).decode()
        buffer += dados

        while "#" in buffer:
            pacote_raw, buffer = buffer.split("#", 1)
            if not pacote_raw.strip():
                continue

            try:
                cabecalho, conteudo, chk_tag = pacote_raw.split("|")
                seq = int(cabecalho.replace("SEQ:", ""))
                chk_recebido = int(chk_tag.replace("CHK:", ""))
                chk_calculado = calcular_checksum(conteudo)
            except Exception:
                print(f"[Server] Erro no formato do pacote: {pacote_raw}")
                conn.send("NACK ?".encode())
                continue

            print(f"[Server] Pacote SEQ {seq} recebido: '{conteudo}' (CHK={chk_recebido})")

            if chk_calculado != chk_recebido:
                print(f"[Server] Erro de integridade no pacote SEQ {seq}: CHK esperado {chk_calculado}, recebido {chk_recebido}")
                conn.send(f"NACK {seq}".encode())
                continue

            if seq - 1 not in recebidos:
                mensagem_reconstruida[seq - 1] = conteudo
                recebidos.add(seq - 1)

            conn.send(f"ACK {seq}".encode())

    mensagem_final = ''.join(p for p in mensagem_reconstruida if p)
    print(f"[Server] Mensagem final reconstruída: {mensagem_final}")
    conn.close()
    server_socket.close()

if __name__ == "__main__":
    start_server()
