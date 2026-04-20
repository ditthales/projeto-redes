import os
import socket

# Este arquivo implementa o cliente UDP do projeto.
# Ele envia um arquivo para o servidor em pacotes de ate 1024 bytes,
# aguarda o retorno do arquivo renomeado e salva em uma pasta local.
#
# O UDP nao confirma entrega, entao usamos um header simples antes dos dados
# binarios. Esse header informa o nome e o tamanho do arquivo, permitindo ao
# receptor saber quando terminou de ler.
#
# Configuracao do cliente e do protocolo
BUFFER_SIZE = 1024
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9000
INPUT_PATH = "input/sample.txt"
OUTPUT_DIR = "client_out"


def make_header(name: str, size: int) -> bytes:
    # Monta o header no formato usado pelo servidor.
    # Esse header eh enviado antes do arquivo para indicar nome e tamanho.
    header_text = f"NAME:{name}\nSIZE:{size}\n"
    return header_text.encode("utf-8")


def parse_header(header_bytes: bytes) -> tuple[str, int]:
    # Decodifica o header com nome e tamanho do arquivo recebido.
    # Isso informa quantos bytes ainda serao recebidos em seguida.
    header_text = header_bytes.decode("utf-8").strip()
    parts = header_text.split("\n")
    name = ""
    size = 0
    for part in parts:
        if part.startswith("NAME:"):
            name = part.replace("NAME:", "", 1).strip()
        elif part.startswith("SIZE:"):
            size_text = part.replace("SIZE:", "", 1).strip()
            size = int(size_text)
    return name, size


def send_file(sock: socket.socket, file_path: str) -> None:
    # 1) Envia header e pacotes do arquivo para o servidor.
    # O arquivo eh lido em blocos de 1024 bytes para simular fragmentacao.
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    sock.sendto(make_header(file_name, file_size), (SERVER_HOST, SERVER_PORT))
    with open(file_path, "rb") as file_in:
        while True:
            chunk = file_in.read(BUFFER_SIZE)
            if not chunk:
                break
            sock.sendto(chunk, (SERVER_HOST, SERVER_PORT))
    print(f"Sent {file_name} ({file_size} bytes) to {SERVER_HOST}:{SERVER_PORT}")


def receive_file(sock: socket.socket) -> str:
    # 2) Recebe o header do arquivo renomeado.
    # Assim o cliente sabe qual sera o nome e o tamanho do arquivo retornado.
    header_bytes, _ = sock.recvfrom(BUFFER_SIZE)
    file_name, expected_size = parse_header(header_bytes)
    if not file_name or expected_size <= 0:
        raise ValueError("Invalid header received")

    # 3) Recebe os pacotes ate completar o tamanho informado.
    # O arquivo eh salvo na pasta client_out.
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, file_name)

    received_size = 0
    with open(output_path, "wb") as file_out:
        while received_size < expected_size:
            chunk, _ = sock.recvfrom(BUFFER_SIZE)
            file_out.write(chunk)
            received_size += len(chunk)

    print(f"Received {file_name} ({received_size} bytes)")
    return output_path


def main() -> None:
    # Valida a existencia do arquivo de entrada antes de iniciar.
    # Isso evita tentar enviar um caminho que nao existe.
    if not os.path.exists(INPUT_PATH):
        raise FileNotFoundError(
            f"Input file not found: {INPUT_PATH}. "
            "Update INPUT_PATH in cliente.py."
        )

    # Envia o arquivo e aguarda o retorno renomeado.
    # O mesmo socket UDP eh usado para envio e recebimento.
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        send_file(sock, INPUT_PATH)
        receive_file(sock)


if __name__ == "__main__":
    # Ponto de entrada do cliente
    main()
