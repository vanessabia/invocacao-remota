"""Servidor de invocação remota usando socket UDP."""
import argparse
import socket

from protocol import (
    MAX_DATAGRAM_SIZE,
    create_reply,
    decode_message,
    encode_message,
)


def execute_operation(operation: str, arguments: list):
    """Executa uma das operações matemáticas disponibilizadas pelo servidor."""
    if not isinstance(arguments, list) or len(arguments) != 2:
        raise ValueError("A operação exige exatamente dois argumentos.")

    a, b = arguments
    if not isinstance(a, (int, float)) or isinstance(a, bool):
        raise ValueError("O primeiro argumento precisa ser numérico.")
    if not isinstance(b, (int, float)) or isinstance(b, bool):
        raise ValueError("O segundo argumento precisa ser numérico.")

    operations = {
        "somar": lambda x, y: x + y,
        "subtrair": lambda x, y: x - y,
        "multiplicar": lambda x, y: x * y,
        "dividir": lambda x, y: x / y,
    }

    if operation not in operations:
        raise ValueError(f"Operação desconhecida: {operation}")
    if operation == "dividir" and b == 0:
        raise ValueError("Não é possível dividir por zero.")

    return operations[operation](a, b)


def process_request(message: dict) -> dict:
    """Valida a requisição e produz a resposta correspondente."""
    request_id = str(message.get("request_id", "sem-id"))
    try:
        if message.get("type") != "request":
            raise ValueError("Tipo de mensagem inválido.")
        operation = message.get("operation")
        arguments = message.get("arguments")
        if not isinstance(operation, str):
            raise ValueError("A operação precisa ser informada como texto.")
        result = execute_operation(operation, arguments)
        return create_reply(request_id, result=result)
    except (ValueError, TypeError, ZeroDivisionError) as exc:
        return create_reply(request_id, error=str(exc))


def serve(host: str = "0.0.0.0", port: int = 5000):
    """Aguarda requisições UDP e devolve uma resposta ao cliente."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.bind((host, port))
        print(f"Servidor UDP ativo em {host}:{port}. Aguardando requisições...")
        while True:
            data, client_address = server_socket.recvfrom(MAX_DATAGRAM_SIZE)
            try:
                request = decode_message(data)
                print(f"Requisição recebida de {client_address}: {request}")
                reply = process_request(request)
            except (UnicodeDecodeError, ValueError) as exc:
                reply = create_reply("desconhecido", error=f"Mensagem inválida: {exc}")

            server_socket.sendto(encode_message(reply), client_address)
            print(f"Resposta enviada para {client_address}: {reply}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Servidor de invocação remota via UDP.")
    parser.add_argument("--host", default="0.0.0.0", help="Endereço para escutar (padrão: 0.0.0.0).")
    parser.add_argument("--port", type=int, default=5000, help="Porta UDP (padrão: 5000).")
    args = parser.parse_args()
    serve(args.host, args.port)
