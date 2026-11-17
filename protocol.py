import json
import uuid

MAX_DATAGRAM_SIZE = 65507


def create_request(operation, arguments, request_id=None):
    return {
        "type": "request",
        "request_id": request_id or str(uuid.uuid4()),
        "operation": operation,
        "arguments": arguments
    }


def create_reply(request_id, result=None, error=None):
    return {
        "type": "reply",
        "request_id": request_id,
        "result": result,
        "error": error
    }


def encode_message(message):
    data = json.dumps(message, ensure_ascii=False).encode("utf-8")

    if len(data) > MAX_DATAGRAM_SIZE:
        raise ValueError("Mensagem excede o limite de um datagrama UDP.")

    return data


def decode_message(data):
    message = json.loads(data.decode("utf-8"))

    if not isinstance(message, dict):
        raise ValueError("A mensagem deve ser um objeto JSON.")

    return message