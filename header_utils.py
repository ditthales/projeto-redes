def make_header(name: str, size: int) -> bytes:
    # Monta header no formato usado pelo servidor
    # Header é enviado antes do arquivo para indicar nome e tamanho
    header_text = f"NAME:{name}\nSIZE:{size}\n"
    return header_text.encode("utf-8")

def parse_header(header_bytes: bytes) -> tuple[str, int]:
    # Decodifica o header simples e extrai nome e tamanho do arquivo
    # O header é uma mensagem de texto enviada antes dos dados binarios,
    # por exemplo: "NAME:foto.png" e "SIZE:24567"
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

