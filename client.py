import os
import socket
from header_utils import *
from project_global import * 

# Este arquivo implementa o cliente UDP do projeto.
# Ele envia um arquivo para o servidor em pacotes de ate 1024 bytes,
# aguarda o retorno do arquivo renomeado e salva em uma pasta local.
#
# O UDP nao confirma entrega, entao usamos um header simples antes dos dados
# binarios. Esse header informa o nome e o tamanho do arquivo, permitindo ao
# receptor saber quando terminou de ler.

def send_file(sock: socket.socket, file_path: str) -> None:
    # Envia header e pacotes do arquivo para o servidor
    # O arquivo eh lido em blocos de 1024 bytes para simular fragmentacao
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    sock.sendto(make_header(file_name, file_size), (SERVER_HOST, SERVER_PORT))
    with open(file_path, "rb") as file_in:
        while True:
            chunk = file_in.read(BUFFER_SIZE)
            if not chunk:
                break
            sock.sendto(chunk, (SERVER_HOST, SERVER_PORT))
    print(f"{file_name} ({file_size} bytes) enviado para {SERVER_HOST}:{SERVER_PORT}")


def receive_file(sock: socket.socket) -> str:
    # Recebe o header do arquivo renomeado
    # Assim o cliente sabe qual sera o nome e o tamanho do arquivo retornado
    header_bytes, _ = sock.recvfrom(BUFFER_SIZE)
    file_name, expected_size = parse_header(header_bytes)
    if not file_name or expected_size <= 0:
        raise ValueError("Header inválido recebido")

    # Recebe os pacotes ate completar o tamanho informado
    # O arquivo eh salvo na pasta client_out
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, file_name)

    received_size = 0
    with open(output_path, "wb") as file_out:
        while received_size < expected_size:
            chunk, _ = sock.recvfrom(BUFFER_SIZE)
            file_out.write(chunk)
            received_size += len(chunk)

    print(f"{file_name} ({received_size} bytes) recebido")
    return output_path

def main() -> None:
    # Valida a existencia do arquivo de entrada antes de iniciar
    # Isso evita tentar enviar um caminho que nao existe
    if not os.path.exists(INPUT_PATH):
        raise FileNotFoundError(
            f"Arquivo de Input não encontrado: {INPUT_PATH}. "
            "Update INPUT_PATH em cliente.py."
        )

    # Envia o arquivo e aguarda o retorno renomeado
    # O mesmo socket UDP é usado para envio e recebimento
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        send_file(sock, INPUT_PATH)
        receive_file(sock)

if __name__ == "__main__":
    # Ponto de entrada do cliente
    main()
