import os
import socket

# Este arquivo implementa o servidor UDP do projeto.
# Ele recebe um arquivo enviado pelo cliente em partes de ate 1024 bytes,
# salva o arquivo no disco, renomeia com o prefixo "leilao_" e devolve o
# arquivo renomeado para o cliente como confirmacao de recebimento.
#
# Como o UDP nao garante entrega, ordem ou integridade, este codigo nao usa
# retransmissao nesta etapa. Para saber quando parar de ler, usamos um header
# inicial com nome e tamanho do arquivo. O servidor continua recebendo ate
# somar exatamente o tamanho informado no header.
#
# Configuracao do protocolo e do servidor
BUFFER_SIZE = 1024
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 9000
DATA_DIR = "data"
PREFIX = "leilao_"


def parse_header(header_bytes: bytes) -> tuple[str, int]:
    # Decodifica o header simples e extrai nome e tamanho do arquivo.
    # O header eh uma pequena mensagem de texto enviada antes dos dados binarios,
    # por exemplo: "NAME:foto.png" e "SIZE:24567".
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


def make_header(name: str, size: int) -> bytes:
    # Monta o header no formato esperado pelo cliente.
    # Essa mensagem diz qual eh o nome do arquivo e quantos bytes virao.
    header_text = f"NAME:{name}\nSIZE:{size}\n"
    return header_text.encode("utf-8")


def receive_file(sock: socket.socket) -> tuple[str, str, tuple[str, int]]:
    # 1) Recebe o header com nome e tamanho.
    # O primeiro pacote nao eh parte do arquivo em si, e sim um aviso.
    header_bytes, client_addr = sock.recvfrom(BUFFER_SIZE)
    original_name, expected_size = parse_header(header_bytes)
    if not original_name or expected_size <= 0:
        raise ValueError("Invalid header received")

    # 2) Garante pasta de destino e prepara caminho do arquivo.
    # O servidor sempre salva em uma pasta fixa dentro do projeto.
    os.makedirs(DATA_DIR, exist_ok=True)
    original_path = os.path.join(DATA_DIR, original_name)

    # 3) Recebe os pacotes ate completar o tamanho indicado.
    # Cada pacote pode ter ate 1024 bytes, entao o arquivo chega em partes.
    received_size = 0
    with open(original_path, "wb") as file_out:
        while received_size < expected_size:
            chunk, _ = sock.recvfrom(BUFFER_SIZE)
            file_out.write(chunk)
            received_size += len(chunk)

    # 4) Renomeia com o prefixo solicitado.
    # Isso comprova que o servidor processou o arquivo antes de devolver.
    renamed_name = f"{PREFIX}{original_name}"
    renamed_path = os.path.join(DATA_DIR, renamed_name)
    if os.path.exists(renamed_path):
        os.remove(renamed_path)
    os.rename(original_path, renamed_path)

    print(
        f"Received {original_name} ({received_size} bytes) from {client_addr}. "
        f"Stored as {renamed_name}."
    )
    return renamed_name, renamed_path, client_addr


def send_file(sock: socket.socket, file_name: str, file_path: str, client_addr: tuple[str, int]) -> None:
    # 5) Envia de volta o arquivo renomeado ao cliente.
    # Reutiliza o mesmo formato: header com nome/tamanho e depois os bytes.
    file_size = os.path.getsize(file_path)
    sock.sendto(make_header(file_name, file_size), client_addr)
    with open(file_path, "rb") as file_in:
        while True:
            chunk = file_in.read(BUFFER_SIZE)
            if not chunk:
                break
            sock.sendto(chunk, client_addr)
    print(f"Sent {file_name} ({file_size} bytes) to {client_addr}.")


def main() -> None:
    # Inicializa o socket UDP e entra no loop de atendimento.
    # O servidor fica aguardando arquivos indefinidamente.
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((SERVER_HOST, SERVER_PORT))
        print(f"Server listening on {SERVER_HOST}:{SERVER_PORT}")
        while True:
            try:
                renamed_name, renamed_path, client_addr = receive_file(sock)
                send_file(sock, renamed_name, renamed_path, client_addr)
            except Exception as exc:
                print(f"Error: {exc}")


if __name__ == "__main__":
    # Ponto de entrada do servidor
    main()
