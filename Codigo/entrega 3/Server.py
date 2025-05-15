import socket

def start_server(host='localhost', port=5050):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)

    print(f"[Server] Aguardando conexão em {host}:{port}...")
    conn, addr = server_socket.accept()
    print(f"[Server] Conectado por {addr}")

    # Handshake
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
                dados = conn.recv(1024).decode()
                if not dados:
                    continue
                buffer += dados

                while "#" in buffer:
                    pacote_bruto, buffer = buffer.split("#", 1)
                    if not pacote_bruto:
                        continue

                    # Tenta extrair sequência
                    if pacote_bruto.startswith("SEQ:"):
                        try:
                            cabecalho, conteudo = pacote_bruto.split("|", 1)
                            seq_num = cabecalho.replace("SEQ:", "")
                        except:
                            seq_num = "?"
                            conteudo = pacote_bruto
                    else:
                        seq_num = "?"
                        conteudo = pacote_bruto

                    print(f"[Server] Pacote recebido (SEQ {seq_num}): {conteudo}")
                    pacotes_recebidos += 1

                    if "ERRO" in conteudo:
                        print(f"[Server] ERRO detectado no Pacote SEQ {seq_num}!")

                    mensagem_reconstruida += conteudo
                    conn.send(f"ACK {seq_num}".encode())

                    if pacotes_recebidos >= num_pacotes:
                        break
            except socket.timeout:
                continue
    except Exception as e:
        print(f"[Server] Erro durante a recepção: {e}")

    print(f"[Server] Mensagem completa reconstruída: {mensagem_reconstruida}")
    conn.close()
    server_socket.close()

if __name__ == "__main__":
    start_server()
