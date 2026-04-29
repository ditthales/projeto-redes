# Primeira Entrega - UDP File Transfer

## Integrantes
- Thales Vinicius Gomes Fraga
- Michelly Emanuela da Silva

## Visão geral
Este projeto implementa transmissão de arquivos via UDP com pacotes de até 1024 bytes. O cliente envia um arquivo para o servidor, o servidor armazena, renomeia com o prefixo "leilao_" e devolve o arquivo renomeado ao cliente.

## Estrutura
- cliente.py: envia o arquivo e recebe o retorno
- servidor.py: recebe, armazena, renomeia e devolve
- data/: pasta fixa para arquivos do servidor
- client_out/: pasta para arquivos retornados ao cliente (criada automaticamente)

## Como executar
1. Em um terminal, execute o servidor:
   python3 servidor.py
2. Em outro terminal, execute o cliente:
   python3 cliente.py

## Configuração
- Em cliente.py, ajuste INPUT_PATH para o arquivo que deseja enviar.
- O servidor escuta em 127.0.0.1:9000 e o cliente envia para 127.0.0.1:9000.

## Testes recomendados
- Enviar um arquivo .txt pequeno
- Enviar uma imagem (.png ou .jpg)

## Observações
- O protocolo usa um header simples com nome e tamanho antes dos bytes do arquivo.
- O tamanho maximo de cada pacote e 1024 bytes (BUFFER_SIZE).
- Codigo comentado e modularizado conforme solicitado.
# projeto-redes
