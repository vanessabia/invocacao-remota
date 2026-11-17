"""Camada de protocolo de invocação remota sobre UDP.

As mensagens são codificadas em JSON e enviadas como datagramas UDP.
"""
import json
import uuid

ENCODING = "utf-8"
MAX_DATAGRAM_SIZE = 65507


def create_request(operation: str, arguments: list, request_id: str | None = None) -> dict:
    """Monta uma requisição identificada para execução remota."""
    return {
        "type": "request",
        "request_id": request_id or str(uuid.uuid4()),
        "operation": operation,
        "arguments": arguments,
    }


def create_reply(request_id: str, result=None, error: str | None = None) -> dict:
    """Monta a resposta do servidor."""
    return {
        "type": "reply",
        "request_id": request_id,
        "result": result,
        "error": error,
    }


def encode_message(message: dict) -> bytes:
    """Serializa uma mensagem em JSON e converte para bytes."""
    return json.dumps(message, ensure_ascii=False).encode(ENCODING)


def decode_message(data: bytes) -> dict:
    """Converte bytes recebidos em uma estrutura Python."""
    message = json.loads(data.decode(ENCODING))
    if not isinstance(message, dict):
        raise ValueError("A mensagem precisa ser um objeto JSON.")
    return message
