import socket
import threading
import unittest
from unittest.mock import patch

import server

from protocol import (
    create_request,
    encode_message,
    decode_message
)

from server import execute_operation, process_request, serve
from client import remote_call


class ProtocolTests(unittest.TestCase):

    def test_encode_decode_round_trip(self):
        message = create_request("somar", [2, 3])

        self.assertEqual(
            decode_message(encode_message(message)),
            message
        )

    def test_operation_sum(self):
        self.assertEqual(execute_operation("somar", [2, 3]), 5)

    def test_operation_subtract(self):
        self.assertEqual(execute_operation("subtrair", [9, 4]), 5)

    def test_operation_multiply(self):
        self.assertEqual(execute_operation("multiplicar", [3, 4]), 12)

    def test_operation_divide(self):
        self.assertEqual(execute_operation("dividir", [8, 2]), 4)

    def test_division_by_zero(self):
        with self.assertRaisesRegex(ValueError, "zero"):
            execute_operation("dividir", [8, 0])

    def test_unknown_operation(self):
        with self.assertRaisesRegex(ValueError, "desconhecida"):
            execute_operation("potencia", [2, 3])

    def test_invalid_argument_count(self):
        with self.assertRaises(ValueError):
            execute_operation("somar", [1])

    def test_process_request_error(self):
        reply = process_request(
            create_request("dividir", [1, 0])
        )

        self.assertIn("zero", reply["error"])


class UDPIntegrationTests(unittest.TestCase):

    def setUp(self):

        self.stop_event = threading.Event()
        self.ready_event = threading.Event()

        self.server_thread = threading.Thread(
            target=serve,
            kwargs={
                "host": "127.0.0.1",
                "port": 0,
                "stop_event": self.stop_event,
                "ready_event": self.ready_event
            },
            daemon=True
        )

        self.server_thread.start()

        self.assertTrue(self.ready_event.wait(2))

        self.port = self.server_thread.server_port

    def tearDown(self):

        self.stop_event.set()
        self.server_thread.join(timeout=2)

    def test_real_udp_round_trip(self):

        result = remote_call(
            "127.0.0.1",
            self.port,
            "somar",
            [10, 5]
        )

        self.assertEqual(result, 15)

    def test_remote_error_is_returned(self):

        with self.assertRaisesRegex(RuntimeError, "zero"):

            remote_call(
                "127.0.0.1",
                self.port,
                "dividir",
                [1, 0]
            )

    def test_duplicate_request_is_not_executed_twice(self):

        request = create_request(
            "somar",
            [4, 6],
            request_id="same-id"
        )

        payload = encode_message(request)

        with patch.object(
            server,
            "execute_operation",
            wraps=server.execute_operation
        ) as operation_mock:

            with socket.socket(
                socket.AF_INET,
                socket.SOCK_DGRAM
            ) as sock:

                sock.settimeout(1)

                sock.sendto(payload, ("127.0.0.1", self.port))

                first = decode_message(
                    sock.recvfrom(65535)[0]
                )

                sock.sendto(payload, ("127.0.0.1", self.port))

                second = decode_message(
                    sock.recvfrom(65535)[0]
                )

            self.assertEqual(first, second)
            self.assertEqual(first["result"], 10)

            # A operação deve ter sido executada somente uma vez.
            operation_mock.assert_called_once()

    def test_multiplication_integration(self):

        result = remote_call(
            "127.0.0.1",
            self.port,
            "multiplicar",
            [6, 7]
        )

        self.assertEqual(result, 42)


if __name__ == "__main__":
    unittest.main()