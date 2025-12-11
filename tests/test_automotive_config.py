"""Tests for Automotive Configuration."""

import unittest
import sys
from unittest.mock import MagicMock

# Mock dependencies
sys.modules['openai'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()

from phone_agent.config.automotive_apps import AUTOMOTIVE_APP_PACKAGES
from phone_agent.config import get_system_prompt
from phone_agent.config.prompts_automotive import AUTOMOTIVE_SYSTEM_PROMPT

class TestAutomotiveConfig(unittest.TestCase):
    def test_automotive_apps_exist(self):
        self.assertIn("高德地图车机版", AUTOMOTIVE_APP_PACKAGES)
        self.assertEqual(AUTOMOTIVE_APP_PACKAGES["高德地图车机版"], "com.autonavi.amapauto")
        self.assertIn("空调", AUTOMOTIVE_APP_PACKAGES)

    def test_get_system_prompt_automotive(self):
        prompt = get_system_prompt("automotive_cn")
        self.assertEqual(prompt, AUTOMOTIVE_SYSTEM_PROMPT)
        self.assertIn("数字座舱自动化测试专家", prompt)
        self.assertIn("安全优先", prompt)

    def test_app_integration(self):
        # Verify that automotive apps are merged into the main APP_PACKAGES
        from phone_agent.config.apps import APP_PACKAGES
        self.assertIn("高德地图车机版", APP_PACKAGES)
        self.assertIn("微信", APP_PACKAGES)

if __name__ == '__main__':
    unittest.main()
