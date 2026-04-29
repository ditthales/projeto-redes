import os
import socket
from project_global import * 
from header_utils import *

# Este arquivo implementa o servidor UDP do projeto.
# Ele recebe um arquivo enviado pelo cliente em partes de ate 1024 bytes,
# salva o arquivo no disco, renomeia com o prefixo "leilao_" e devolve o
# arquivo renomeado para o cliente como confirmacao de recebimento.
#
# Como o UDP nao garante entrega, ordem ou integridade, este codigo nao usa
# retransmissao nesta etapa. Para saber quando parar de ler, usamos um header
# inicial com nome e tamanho do arquivo. O servidor continua recebendo ate
# somar exatamente o tamanho informado no header.

def send_file(sock: socket.socket, file_name: str, file_path: str, client_addr: tuple[str, int]) -> None:
    # Envia de volta o arquivo renomeado ao cliente
    # Reutiliza o mesmo formato: header com nome/tamanho e depois os bytes
    file_size = os.path.getsize(file_path)
    sock.sendto(make_header(file_name, file_size), client_addr)
    with open(file_path, "rb") as file_in:
        while True:
            chunk = file_in.read(BUFFER_SIZE)
            if not chunk:
                break
            sock.sendto(chunk, client_addr)
    print(f"{file_name} ({file_size} bytes) enviado para {client_addr}.")

def receive_file(sock: socket.socket) -> tuple[str, str, tuple[str, int]]:
    # Recebe header com nome e tamanho
    # O primeiro pacote não é parte do arquivo em si, e sim um aviso
    header_bytes, client_addr = sock.recvfrom(BUFFER_SIZE)
    original_name, expected_size = parse_header(header_bytes)
    if not original_name or expected_size <= 0:
        raise ValueError("Header inválido recebido")

    # Garante pasta de destino e prepara caminho do arquivo
    # O servidor sempre salva em uma pasta fixa dentro do projeto
    os.makedirs(DATA_DIR, exist_ok=True)
    original_path = os.path.join(DATA_DIR, original_name)

    # Recebe os pacotes até completar o tamanho indicado
    # Cada pacote pode ter até 1024 bytes, então o arquivo chega em partes
    received_size = 0
    with open(original_path, "wb") as file_out:
        while received_size < expected_size:
            chunk, _ = sock.recvfrom(BUFFER_SIZE)
            file_out.write(chunk)
            received_size += len(chunk)

    # Renomeia com o prefixo solicitado
    # Isso comprova que o servidor processou o arquivo antes de devolver
    renamed_name = f"{PREFIX}{original_name}"
    renamed_path = os.path.join(DATA_DIR, renamed_name)
    if os.path.exists(renamed_path):
        os.remove(renamed_path)
    os.rename(original_path, renamed_path)

    print(
        f"{original_name} ({received_size} bytes) recebido de {client_addr}. "
        f"Salvo como {renamed_name}."
    )
    return renamed_name, renamed_path, client_addr

def main() -> None:
    # Inicializa o socket UDP e entra no loop de atendimento
    # O servidor fica aguardando arquivos indefinidamente
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((SERVER_HOST, SERVER_PORT))
        print(f"Servidor ouvindo em {SERVER_HOST}:{SERVER_PORT}")
        while True:
            try:
                renamed_name, renamed_path, client_addr = receive_file(sock)
                send_file(sock, renamed_name, renamed_path, client_addr)
            except Exception as exc:
                print(f"Erro: {exc}")


if __name__ == "__main__":
    # Ponto de entrada do servidor
    main()
