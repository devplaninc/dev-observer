import json
import unittest
from dataclasses import dataclass

from dev_observer.log import StackdriverEncoder, StructuredMessage, DataclassJSONEncoder

@dataclass
class MyDataClass:
    field1: str
    field2: int

class TestStackdriverEncoder(unittest.TestCase):

    def setUp(self):
        self.encoder = StackdriverEncoder()

    def test_basic_message_info_severity(self):
        msg = StructuredMessage("Test info message", level="INFO")
        encoded_json_str = self.encoder.encode(msg)
        decoded = json.loads(encoded_json_str)

        self.assertEqual(decoded["message"], "Test info message")
        self.assertEqual(decoded["severity"], "INFO")

    def test_message_warning_severity_and_extra_args(self):
        msg = StructuredMessage("Test warning", key="value", another_key=123, level="WARNING")
        encoded_json_str = self.encoder.encode(msg)
        decoded = json.loads(encoded_json_str)

        self.assertEqual(decoded["message"], "Test warning")
        self.assertEqual(decoded["severity"], "WARNING")
        self.assertEqual(decoded["key"], "value")
        self.assertEqual(decoded["another_key"], 123)
        self.assertNotIn("level", decoded) # 'level' should be consumed and not in top-level output

    def test_message_error_severity(self):
        msg = StructuredMessage("Test error", level="ERROR")
        encoded_json_str = self.encoder.encode(msg)
        decoded = json.loads(encoded_json_str)

        self.assertEqual(decoded["message"], "Test error")
        self.assertEqual(decoded["severity"], "ERROR")

    def test_message_default_severity_when_level_missing(self):
        msg = StructuredMessage("Test default level")
        encoded_json_str = self.encoder.encode(msg)
        decoded = json.loads(encoded_json_str)

        self.assertEqual(decoded["message"], "Test default level")
        # As per StackdriverEncoder implementation, severity defaults to "INFO"
        self.assertEqual(decoded["severity"], "INFO")

    def test_message_unknown_level_defaults_to_info(self):
        msg = StructuredMessage("Test unknown level", level="UNHEARD_OF_LEVEL")
        encoded_json_str = self.encoder.encode(msg)
        decoded = json.loads(encoded_json_str)

        self.assertEqual(decoded["message"], "Test unknown level")
        self.assertEqual(decoded["severity"], "INFO") # Default severity

    def test_message_with_dataclass_in_kwargs(self):
        data_obj = MyDataClass(field1="hello", field2=42)
        msg = StructuredMessage("Message with dataclass", data=data_obj, level="DEBUG")
        encoded_json_str = self.encoder.encode(msg)
        decoded = json.loads(encoded_json_str)

        self.assertEqual(decoded["message"], "Message with dataclass")
        self.assertEqual(decoded["severity"], "DEBUG")
        self.assertIn("data", decoded)
        self.assertIsInstance(decoded["data"], dict)
        self.assertEqual(decoded["data"]["field1"], "hello")
        self.assertEqual(decoded["data"]["field2"], 42)

    def test_level_kwarg_case_insensitivity(self):
        msg = StructuredMessage("Test case insensitive level", level="wArNiNg")
        encoded_json_str = self.encoder.encode(msg)
        decoded = json.loads(encoded_json_str)

        self.assertEqual(decoded["message"], "Test case insensitive level")
        self.assertEqual(decoded["severity"], "WARNING")

    def test_empty_message_and_kwargs(self):
        msg = StructuredMessage("", level="CRITICAL")
        encoded_json_str = self.encoder.encode(msg)
        decoded = json.loads(encoded_json_str)

        self.assertEqual(decoded["message"], "")
        self.assertEqual(decoded["severity"], "CRITICAL")
        # Ensure no other keys apart from message and severity are present if kwargs (excluding level) are empty
        self.assertEqual(len(decoded.keys()), 2)


if __name__ == '__main__':
    unittest.main()
