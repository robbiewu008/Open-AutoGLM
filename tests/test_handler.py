"""Tests for the ActionHandler and action parsing."""

import unittest
import sys
from unittest.mock import MagicMock

# Mock dependencies to avoid installation requirement for unit tests
sys.modules['openai'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()

from phone_agent.actions.handler import parse_action, ActionHandler

class TestActionParsing(unittest.TestCase):
    def test_parse_valid_tap(self):
        response = 'do(action="Tap", element=[500, 300])'
        expected = {'_metadata': 'do', 'action': 'Tap', 'element': [500, 300]}
        self.assertEqual(parse_action(response), expected)

    def test_parse_valid_type(self):
        response = 'do(action="Type", text="Hello World")'
        expected = {'_metadata': 'do', 'action': 'Type', 'text': 'Hello World'}
        self.assertEqual(parse_action(response), expected)

    def test_parse_valid_finish(self):
        response = 'finish(message="Task completed successfully")'
        expected = {'_metadata': 'finish', 'message': 'Task completed successfully'}
        self.assertEqual(parse_action(response), expected)

    def test_parse_finish_with_quotes(self):
        response = "finish(message='Task completed')"
        expected = {'_metadata': 'finish', 'message': 'Task completed'}
        self.assertEqual(parse_action(response), expected)

    def test_malicious_code_execution(self):
        # This should fail with the new parser, or at least not execute the code
        # The new parser uses ast.literal_eval, so it shouldn't execute os.system
        response = 'do(action=__import__("os").system("echo malicious"))'
        with self.assertRaises(ValueError):
            parse_action(response)

    def test_malicious_eval(self):
        response = 'do(action="Tap", element=eval("__import__(\'os\').system(\'echo malicious\')"))'
        with self.assertRaises(ValueError):
             parse_action(response)

class TestResolutionScaling(unittest.TestCase):
    def setUp(self):
        # Mock adb.tap and others since ActionHandler imports them
        sys.modules['phone_agent.adb'] = MagicMock()
        self.handler = ActionHandler()

    def test_scale_mobile_portrait(self):
        # 1080x2400 (Mobile Portrait)
        width, height = 1080, 2400
        # Center of screen (500, 500 relative)
        relative = [500, 500]
        expected = (540, 1200)
        result = self.handler._convert_relative_to_absolute(relative, width, height)
        self.assertEqual(result, expected)

    def test_scale_automotive_landscape(self):
        # 1920x720 (Automotive Landscape)
        width, height = 1920, 720
        # Center of screen (500, 500 relative)
        relative = [500, 500]
        expected = (960, 360)
        result = self.handler._convert_relative_to_absolute(relative, width, height)
        self.assertEqual(result, expected)

    def test_scale_automotive_ultrawide(self):
        # 2560x1080 (Ultrawide)
        width, height = 2560, 1080
        # Top-left corner (100, 100 relative)
        relative = [100, 100]
        expected = (256, 108)
        result = self.handler._convert_relative_to_absolute(relative, width, height)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
