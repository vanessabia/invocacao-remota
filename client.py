import argparse
import socket

from protocol import create_request, decode_message, encode_message


def remote_call(host, port, operation, arguments, timeout=2.0, retries=2):

    request = create_request(operation, arguments)
    payload = encode_message(request)

    last_error = None

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:

        sock.settimeout(timeout)

        for attempt in range(retries + 1):

            try:
                sock.sendto(payload, (host, port))

                while True:

                    data, _ = sock.recvfrom(65535)

                    reply = decode_message(data)

                    if (
                        reply.get("type") == "reply"
                        and reply.get("request_id") == request["request_id"]
                    ):

                        if reply.get("error"):
                            raise RuntimeError(reply["error"])

                        return reply.get("result")

            except (socket.timeout, ConnectionResetError, OSError) as error:
                last_error = error

        raise TimeoutError(
            f"Servidor {host}:{port} não respondeu após "
            f"{retries + 1} tentativas. Último erro: {last_error}"
        )


def main():

    parser = argparse.ArgumentParser(
        description="Cliente de invocação remota UDP"
    )

    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)

    parser.add_argument(
        "--operation",
        choices=["somar", "subtrair", "multiplicar", "dividir"],
        required=True
    )

    parser.add_argument("--a", type=float, required=True)
    parser.add_argument("--b", type=float, required=True)

    args = parser.parse_args()

    try:

        result = remote_call(
            args.host,
            args.port,
            args.operation,
            [args.a, args.b]
        )

        print(f"Resultado: {result}")

    except Exception as error:
        print(f"Erro: {error}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()