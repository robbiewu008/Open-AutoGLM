"""Tests for ADB Retry Logic and Input Routing."""

import unittest
import subprocess
from unittest.mock import patch, MagicMock
import sys

# Mock dependencies
sys.modules['openai'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()

from phone_agent.adb.device import tap, swipe
from phone_agent.utils import retry

class TestADBRetry(unittest.TestCase):
    @patch('subprocess.run')
    def test_retry_success_after_failure(self, mock_run):
        # Setup mock to fail twice then succeed
        mock_run.side_effect = [
            subprocess.TimeoutExpired(cmd='adb', timeout=5),
            subprocess.CalledProcessError(returncode=1, cmd='adb', stderr='error'),
            MagicMock(returncode=0, stdout='success')
        ]

        # Use a dummy retriable function for testing the decorator directly
        @retry(retries=3, delay=0.01, exceptions=(subprocess.TimeoutExpired, subprocess.CalledProcessError))
        def flaky_func():
            return subprocess.run(['adb', 'test'], check=True)

        result = flaky_func()
        self.assertEqual(mock_run.call_count, 3)
        self.assertEqual(result.returncode, 0)

    @patch('subprocess.run')
    def test_retry_max_failures(self, mock_run):
        # Setup mock to fail always
        mock_run.side_effect = subprocess.TimeoutExpired(cmd='adb', timeout=5)

        @retry(retries=2, delay=0.01, exceptions=(subprocess.TimeoutExpired,))
        def always_fail():
            return subprocess.run(['adb', 'test'], check=True)

        with self.assertRaises(subprocess.TimeoutExpired):
            always_fail()
        
        # 1 initial call + 2 retries = 3 total calls
        self.assertEqual(mock_run.call_count, 3)

class TestInputRouting(unittest.TestCase):
    @patch('subprocess.run')
    def test_tap_with_display_id(self, mock_run):
        # Mock successful execution
        mock_run.return_value = MagicMock(returncode=0)
        
        display_id = 2
        x, y = 100, 200
        tap(x, y, display_id=display_id)
        
        # Verify the call args include -d 2
        args = mock_run.call_args[0][0]
        # Expected: ['adb', 'shell', 'input', '-d', '2', 'tap', '100', '200']
        self.assertIn('-d', args)
        self.assertIn('2', args)
        self.assertIn('tap', args)

    @patch('subprocess.run')
    def test_swipe_with_display_id(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        
        display_id = 1
        swipe(100, 100, 200, 200, duration_ms=500, display_id=display_id)
        
        args = mock_run.call_args[0][0]
        self.assertIn('-d', args)
        self.assertIn('1', args)
        self.assertIn('swipe', args)

if __name__ == '__main__':
    unittest.main()
