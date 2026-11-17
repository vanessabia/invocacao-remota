"""Cliente de invocação remota usando socket UDP."""
import argparse
import socket

from protocol import (
    MAX_DATAGRAM_SIZE,
    create_request,
    decode_message,
    encode_message,
)


def remote_call(host: str, port: int, operation: str, arguments: list,
                timeout: float = 3.0, retries: int = 2):
    """Invoca uma operação remota e aguarda a resposta.

    Em caso de perda de pacote, a requisição é retransmitida até o limite
    configurado. O mesmo request_id é mantido nas tentativas.
    """
    request = create_request(operation, arguments)
    payload = encode_message(request)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
        client_socket.settimeout(timeout)

        for attempt in range(retries + 1):
            client_socket.sendto(payload, (host, port))
            try:
                while True:
                    data, _server_address = client_socket.recvfrom(MAX_DATAGRAM_SIZE)
                    reply = decode_message(data)
                    if (reply.get("type") == "reply"
                            and reply.get("request_id") == request["request_id"]):
                        if reply.get("error"):
                            raise RuntimeError(reply["error"])
                        return reply.get("result")
            except socket.timeout:
                if attempt == retries:
                    raise TimeoutError(
                        f"O servidor {host}:{port} não respondeu após "
                        f"{retries + 1} tentativa(s)."
                    )
    raise TimeoutError("Não foi possível obter resposta do servidor.")


def main():
    parser = argparse.ArgumentParser(description="Cliente de invocação remota via UDP.")
    parser.add_argument("--host", default="127.0.0.1", help="IP ou nome do servidor.")
    parser.add_argument("--port", type=int, default=5000, help="Porta UDP do servidor.")
    parser.add_argument("--operation", choices=["somar", "subtrair", "multiplicar", "dividir"],
                        help="Operação remota.")
    parser.add_argument("--a", type=float, help="Primeiro número.")
    parser.add_argument("--b", type=float, help="Segundo número.")
    args = parser.parse_args()

    operation = args.operation or input("Operação (somar, subtrair, multiplicar, dividir): ").strip()
    a = args.a if args.a is not None else float(input("Primeiro número: "))
    b = args.b if args.b is not None else float(input("Segundo número: "))

    try:
        result = remote_call(args.host, args.port, operation, [a, b])
        print(f"Resultado recebido do servidor: {result}")
    except (RuntimeError, TimeoutError, OSError, ValueError) as exc:
        print(f"Falha na invocação remota: {exc}")


if __name__ == "__main__":
    main()
