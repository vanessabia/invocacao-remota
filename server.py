import argparse
import socket
import threading
from collections import OrderedDict

from protocol import create_reply, decode_message, encode_message


CACHE_LIMIT = 1000


def execute_operation(operation, arguments):

    if not isinstance(arguments, list) or len(arguments) != 2:
        raise ValueError("A operação exige exatamente dois argumentos.")

    a, b = arguments

    if isinstance(a, bool) or isinstance(b, bool):
        raise ValueError("Os argumentos devem ser numéricos.")

    try:
        a = float(a)
        b = float(b)
    except (TypeError, ValueError):
        raise ValueError("Os argumentos devem ser numéricos.")

    operations = {
        "somar": lambda: a + b,
        "subtrair": lambda: a - b,
        "multiplicar": lambda: a * b,
        "dividir": lambda: a / b
    }

    if operation not in operations:
        raise ValueError(f"Operação desconhecida: {operation}")

    if operation == "dividir" and b == 0:
        raise ValueError("Não é possível dividir por zero.")

    result = operations[operation]()

    if result.is_integer():
        return int(result)

    return result


def process_request(message):

    request_id = (
        message.get("request_id")
        if isinstance(message, dict)
        else None
    )

    if not isinstance(message, dict) or message.get("type") != "request":
        return create_reply(
            request_id,
            error="Formato de requisição inválido."
        )

    try:
        result = execute_operation(
            message.get("operation"),
            message.get("arguments")
        )

        return create_reply(request_id, result=result)

    except (ValueError, TypeError, ZeroDivisionError) as error:
        return create_reply(request_id, error=str(error))


def get_request(sock):
    data, address = sock.recvfrom(65535)
    return data, address


def send_reply(sock, reply, address):
    sock.sendto(encode_message(reply), address)


def serve(host="0.0.0.0", port=5000, stop_event=None, ready_event=None):

    cache = OrderedDict()

    stop_event = stop_event or threading.Event()

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:

        sock.bind((host, port))
        sock.settimeout(0.2)

        actual_port = sock.getsockname()[1]

        threading.current_thread().server_port = actual_port

        print(f"Servidor UDP ativo em {host}:{actual_port}")

        if ready_event:
            ready_event.set()

        while not stop_event.is_set():

            try:
                data, address = get_request(sock)

            except socket.timeout:
                continue

            except OSError:
                continue

            try:
                message = decode_message(data)

                request_id = (
                    message.get("request_id")
                    if isinstance(message, dict)
                    else None
                )

                key = (address, request_id)

                # Verifica se a requisição já foi processada.
                if request_id is not None and key in cache:
                    reply = cache[key]

                else:
                    reply = process_request(message)

                    if request_id is not None:
                        cache[key] = reply
                        cache.move_to_end(key)

                        # Limita o tamanho do cache.
                        while len(cache) > CACHE_LIMIT:
                            cache.popitem(last=False)

            except (ValueError, UnicodeDecodeError):
                reply = create_reply(
                    None,
                    error="Mensagem JSON inválida."
                )

            try:
                send_reply(sock, reply, address)

            except OSError:
                continue


def main():

    parser = argparse.ArgumentParser(
        description="Servidor de invocação remota UDP"
    )

    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=5000)

    args = parser.parse_args()

    serve(args.host, args.port)


if __name__ == "__main__":
    main()