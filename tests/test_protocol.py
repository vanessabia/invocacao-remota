import unittest

from protocol import create_request, create_reply, encode_message, decode_message
from server import execute_operation, process_request


class ProtocolTests(unittest.TestCase):
    def test_encode_and_decode(self):
        original = create_request("somar", [2, 3], request_id="teste-1")
        self.assertEqual(decode_message(encode_message(original)), original)

    def test_create_reply(self):
        reply = create_reply("abc", result=5)
        self.assertEqual(reply["type"], "reply")
        self.assertEqual(reply["request_id"], "abc")
        self.assertEqual(reply["result"], 5)
        self.assertIsNone(reply["error"])


class RemoteOperationTests(unittest.TestCase):
    def test_add(self):
        self.assertEqual(execute_operation("somar", [2, 3]), 5)

    def test_subtract(self):
        self.assertEqual(execute_operation("subtrair", [8, 3]), 5)

    def test_multiply(self):
        self.assertEqual(execute_operation("multiplicar", [4, 3]), 12)

    def test_divide(self):
        self.assertEqual(execute_operation("dividir", [10, 2]), 5)

    def test_division_by_zero(self):
        with self.assertRaises(ValueError):
            execute_operation("dividir", [10, 0])

    def test_unknown_operation(self):
        with self.assertRaises(ValueError):
            execute_operation("potencia", [2, 3])

    def test_process_request(self):
        request = create_request("somar", [10, 5], request_id="req-10")
        reply = process_request(request)
        self.assertEqual(reply["request_id"], "req-10")
        self.assertEqual(reply["result"], 15)
        self.assertIsNone(reply["error"])

    def test_process_invalid_request(self):
        reply = process_request({"type": "request", "request_id": "x",
                                 "operation": "dividir", "arguments": [1, 0]})
        self.assertIsNotNone(reply["error"])


if __name__ == "__main__":
    unittest.main()
