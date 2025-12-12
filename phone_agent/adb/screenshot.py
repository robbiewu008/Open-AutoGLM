import base64
import os
import subprocess
import tempfile
import uuid
from dataclasses import dataclass
from io import BytesIO
from typing import Tuple

from PIL import Image

from phone_agent.adb.device import get_screen_dimensions # Import the new function
from phone_agent.log import logger


@dataclass
class Screenshot:
    """Represents a captured screenshot."""

    base64_data: str
    width: int
    height: int
    is_sensitive: bool = False


def get_screenshot(device_id: str | None = None, display_id: int = 0, timeout: int = 10) -> Screenshot:
    """
    Capture a screenshot from the connected Android device.

    Args:
        device_id: Optional ADB device ID for multi-device setups.
        display_id: Optional display ID for multi-screen setups (default 0 for primary).
        timeout: Timeout in seconds for screenshot operations.

    Returns:
        Screenshot object containing base64 data and dimensions.

    Note:
        If the screenshot fails (e.g., on sensitive screens like payment pages),
        a black fallback image is returned with is_sensitive=True.
    """
    temp_path = os.path.join(tempfile.gettempdir(), f"screenshot_{uuid.uuid4()}.png")
    adb_prefix = _get_adb_prefix(device_id)

    try:
        # Push to /data/local/tmp as /sdcard/tmp might not be writable on all AAOS versions
        remote_path = f"/data/local/tmp/screenshot_{display_id}_{uuid.uuid4()}.png"

        # Execute screenshot command with display_id
        result = subprocess.run(
            adb_prefix + ["shell", "screencap", "-p", "-d", str(display_id), remote_path],
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        # Check for screenshot failure (sensitive screen)
        output = result.stdout + result.stderr
        if "Status: -1" in output or "Failed" in output:
            return _create_fallback_screenshot(is_sensitive=True, device_id=device_id)

        # Pull screenshot to local temp path
        pull_result = subprocess.run(
            adb_prefix + ["pull", remote_path, temp_path],
            capture_output=True,
            text=True,
            timeout=5,
        )

        # Clean up remote file
        subprocess.run(
            adb_prefix + ["shell", "rm", remote_path],
            capture_output=True,
            text=True,
            timeout=5,
        )
        
        if pull_result.returncode != 0 or not os.path.exists(temp_path):
            logger.error(f"Error pulling screenshot or file not found: {pull_result.stderr}")
            return _create_fallback_screenshot(is_sensitive=False, device_id=device_id)

        # Read and encode image
        img = Image.open(temp_path)
        width, height = img.size

        buffered = BytesIO()
        img.save(buffered, format="PNG")
        base64_data = base64.b64encode(buffered.getvalue()).decode("utf-8")

        # Cleanup
        os.remove(temp_path)

        return Screenshot(
            base64_data=base64_data, width=width, height=height, is_sensitive=False
        )

    except Exception as e:
        logger.error(f"Screenshot error: {e}")
        return _create_fallback_screenshot(is_sensitive=False, device_id=device_id)


def _get_adb_prefix(device_id: str | None) -> list:
    """Get ADB command prefix with optional device specifier."""
    if device_id:
        return ["adb", "-s", device_id]
    return ["adb"]


def _create_fallback_screenshot(is_sensitive: bool, device_id: str | None = None) -> Screenshot:
    """
    Create a black fallback image when screenshot fails, using device dimensions if possible.
    """
    dims = get_screen_dimensions(device_id)
    # Default to common automotive landscape (1920x1080) if device dims cannot be retrieved
    width, height = dims if dims else (1920, 1080) 

    black_img = Image.new("RGB", (width, height), color="black")
    buffered = BytesIO()
    black_img.save(buffered, format="PNG")
    base64_data = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return Screenshot(
        base64_data=base64_data,
        width=width,
        height=height,
        is_sensitive=is_sensitive,
    )
