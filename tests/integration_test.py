"""Integration test for the Phone Agent."""

import unittest
from unittest.mock import MagicMock, patch
import sys
import json

# Mock dependencies
sys.modules['openai'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()

from phone_agent.agent import PhoneAgent, AgentConfig
from phone_agent.model import ModelConfig, ModelResponse

class TestPhoneAgentIntegration(unittest.TestCase):
    @patch('phone_agent.agent.get_screenshot')
    @patch('phone_agent.agent.get_current_app')
    @patch('phone_agent.model.client.ModelClient.request')
    @patch('phone_agent.actions.handler.tap')
    def test_agent_run_flow(self, mock_tap, mock_model_request, mock_get_app, mock_get_screenshot):
        # Setup mocks
        mock_screenshot = MagicMock()
        mock_screenshot.base64_data = "base64_image_data"
        mock_screenshot.width = 1080
        mock_screenshot.height = 2400
        mock_get_screenshot.return_value = mock_screenshot
        
        mock_get_app.return_value = "System Home"
        
        # Simulate model response: "Tap at (500, 500)" -> do(action="Tap", element=[500, 500])
        # Then "finish" -> finish(message="Done")
        
        # We need to simulate a sequence of responses for multiple steps
        # Step 1: User prompt -> Agent gets screen -> Model says "Tap"
        # Step 2: Agent acts -> Agent gets screen -> Model says "Finish"
        
        response1 = ModelResponse(
            thinking="I need to tap the button.",
            action='do(action="Tap", element=[500, 500])',
            raw_content="..."
        )
        response2 = ModelResponse(
            thinking="Task done.",
            action='finish(message="Success")',
            raw_content="..."
        )
        
        mock_model_request.side_effect = [response1, response2]

        # Setup agent
        model_config = ModelConfig()
        agent_config = AgentConfig(max_steps=5, device_id="test_device", display_id=1)
        agent = PhoneAgent(model_config, agent_config)

        # Run agent
        result = agent.run("Test Task")

        # Verifications
        self.assertEqual(result, "Success")
        
        # Verify screenshot was called with correct display_id
        mock_get_screenshot.assert_called_with(device_id="test_device", display_id=1)
        
        # Verify tap was called with correct coordinates and display_id
        # Relative [500, 500] -> Absolute [540, 1200] for 1080x2400
        mock_tap.assert_called_with(540, 1200, "test_device", display_id=1)
        
        # Verify step count
        self.assertEqual(agent.step_count, 2)

if __name__ == '__main__':
    unittest.main()
