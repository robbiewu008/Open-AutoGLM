"""Tests for CLI Configuration and AgentConfig."""

import unittest
import sys
from unittest.mock import MagicMock

# Mock dependencies
sys.modules['openai'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()

from phone_agent.agent import AgentConfig

class TestAgentConfig(unittest.TestCase):
    def test_default_config(self):
        config = AgentConfig()
        self.assertEqual(config.lang, "cn")
        self.assertEqual(config.display_id, 0)

    def test_automotive_config(self):
        config = AgentConfig(lang="automotive_cn", display_id=2)
        self.assertEqual(config.lang, "automotive_cn")
        self.assertEqual(config.display_id, 2)
        # Verify system prompt loading (requires mocking get_system_prompt or checking side effect)
        # Since post_init loads the prompt, we can check if system_prompt is not None
        self.assertIsNotNone(config.system_prompt)

if __name__ == '__main__':
    unittest.main()
