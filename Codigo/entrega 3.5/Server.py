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

    mensagem_reconstruida = ""
    buffer = ""
    pacotes_recebidos = 0
    conn.settimeout(2)

    try:
        while pacotes_recebidos < num_pacotes:
            try:
                dados_recebidos = conn.recv(1024).decode()
                if not dados_recebidos:
                    continue
                buffer += dados_recebidos

                while "#" in buffer:
                    pacote_bruto, buffer = buffer.split("#", 1)
                    if not pacote_bruto.strip():
                        continue

                    try:
                        cabecalho, dados, chk_tag = pacote_bruto.split("|")
                        seq = cabecalho.replace("SEQ:", "")
                        chk_recebido = int(chk_tag.replace("CHK:", ""))
                        chk_calculado = calcular_checksum(dados)
                    except ValueError as ve:
                        print(f"[Server] Erro no formato do pacote: {pacote_bruto}")
                        conn.send("NACK ?".encode())
                        continue

                    print(f"[Server] Pacote SEQ {seq} recebido: '{dados}' (CHK={chk_recebido})")

                    if chk_calculado != chk_recebido:
                        print(f"[Server] Erro de integridade no pacote SEQ {seq}: CHK esperado {chk_calculado}, recebido {chk_recebido}")
                        conn.send(f"NACK {seq}".encode())
                        continue  # NÃO adiciona à mensagem, nem conta o pacote

                    mensagem_reconstruida += dados
                    pacotes_recebidos += 1
                    conn.send(f"ACK {seq}".encode())

                    if pacotes_recebidos >= num_pacotes:
                        break
            except socket.timeout:
                continue
    except Exception as e:
        print(f"[Server] Erro durante recepção: {e}")

    print(f"[Server] Mensagem final reconstruída: {mensagem_reconstruida}")
    conn.close()
    server_socket.close()

if __name__ == "__main__":
    start_server()
