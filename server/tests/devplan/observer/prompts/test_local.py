import unittest
import tempfile
import os
from unittest.mock import Mock

from dev_observer.api.types.ai_pb2 import PromptTemplate, SystemMessage, UserMessage, PromptConfig
from dev_observer.prompts.local import LocalPromptsProvider, TomlPromptTemplateParser, replace_template_parameters


class TestReplaceTemplateParameters(unittest.TestCase):
    def test_replace_single_parameter(self):
        text = "Hello {{name}}, how are you?"
        params = {"name": "John"}
        result = replace_template_parameters(text, params)
        self.assertEqual(result, "Hello John, how are you?")

    def test_replace_multiple_parameters(self):
        text = "Hello {{name}}, you are {{ age }} years old and live in {{city}}."
        params = {"name": "Alice", "age": "25", "city": "New York"}
        result = replace_template_parameters(text, params)
        self.assertEqual(result, "Hello Alice, you are 25 years old and live in New York.")

    def test_replace_parameter_not_found(self):
        text = "Hello {{name}}, you are {{age}} years old."
        params = {"name": "Bob"}
        result = replace_template_parameters(text, params)
        self.assertEqual(result, "Hello Bob, you are {{age}} years old.")

    def test_replace_no_parameters_in_text(self):
        text = "Hello world, no parameters here."
        params = {"name": "John"}
        result = replace_template_parameters(text, params)
        self.assertEqual(result, "Hello world, no parameters here.")

    def test_replace_empty_params(self):
        text = "Hello {{name}}, how are you?"
        params = {}
        result = replace_template_parameters(text, params)
        self.assertEqual(result, "Hello {{name}}, how are you?")

    def test_replace_none_params(self):
        text = "Hello {{name}}, how are you?"
        result = replace_template_parameters(text, None)
        self.assertEqual(result, "Hello {{name}}, how are you?")

    def test_replace_empty_text(self):
        text = ""
        params = {"name": "John"}
        result = replace_template_parameters(text, params)
        self.assertEqual(result, "")

    def test_replace_none_text(self):
        params = {"name": "John"}
        result = replace_template_parameters(None, params)
        self.assertIsNone(result)

    def test_replace_parameter_with_spaces(self):
        text = "Hello {{ name }}, how are you?"
        params = {"name": "John"}
        result = replace_template_parameters(text, params)
        self.assertEqual(result, "Hello John, how are you?")

    def test_replace_same_parameter_multiple_times(self):
        text = "{{greeting}} {{name}}, {{greeting}} again!"
        params = {"greeting": "Hello", "name": "World"}
        result = replace_template_parameters(text, params)
        self.assertEqual(result, "Hello World, Hello again!")
