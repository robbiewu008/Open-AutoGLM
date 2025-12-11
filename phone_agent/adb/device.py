"""Device control utilities for Android automation."""

import os
import subprocess
import time
from typing import List, Optional, Tuple

from phone_agent.config.apps import APP_PACKAGES
from phone_agent.log import logger


def get_current_app(device_id: str | None = None) -> str:
    """
    Get the currently focused app name.

    Args:
        device_id: Optional ADB device ID for multi-device setups.

    Returns:
        The app name if recognized, otherwise "System Home".
    """
    adb_prefix = _get_adb_prefix(device_id)

    try:
        result = subprocess.run(
            adb_prefix + ["shell", "dumpsys", "window"], 
            capture_output=True, 
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            logger.warning(f"Failed to get current app: {result.stderr}")
            return "System Home"
            
        output = result.stdout

        # Parse window focus info
        for line in output.split("\n"):
            if "mCurrentFocus" in line or "mFocusedApp" in line:
                for app_name, package in APP_PACKAGES.items():
                    if package in line:
                        return app_name

        return "System Home"
        
    except subprocess.TimeoutExpired:
        logger.error("Timeout getting current app")
        return "System Home"
    except Exception as e:
        logger.error(f"Error getting current app: {e}")
        return "System Home"


def tap(x: int, y: int, device_id: str | None = None, delay: float = 1.0) -> None:
    """
    Tap at the specified coordinates.

    Args:
        x: X coordinate.
        y: Y coordinate.
        device_id: Optional ADB device ID.
        delay: Delay in seconds after tap.
    """
    adb_prefix = _get_adb_prefix(device_id)
    
    logger.info(f"Tapping at ({x}, {y}) on device {device_id or 'default'}")

    try:
        subprocess.run(
            adb_prefix + ["shell", "input", "tap", str(x), str(y)], 
            capture_output=True,
            timeout=5,
            check=True
        )
        time.sleep(delay)
    except subprocess.TimeoutExpired:
        logger.error(f"Timeout tapping at ({x}, {y})")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to tap at ({x}, {y}): {e.stderr}")
    except Exception as e:
        logger.error(f"Error tapping: {e}")


def double_tap(
    x: int, y: int, device_id: str | None = None, delay: float = 1.0
) -> None:
    """
    Double tap at the specified coordinates.

    Args:
        x: X coordinate.
        y: Y coordinate.
        device_id: Optional ADB device ID.
        delay: Delay in seconds after double tap.
    """
    adb_prefix = _get_adb_prefix(device_id)

    logger.info(f"Double tapping at ({x}, {y}) on device {device_id or 'default'}")

    try:
        subprocess.run(
            adb_prefix + ["shell", "input", "tap", str(x), str(y)], 
            capture_output=True,
            timeout=5,
            check=True
        )
        time.sleep(0.1)
        subprocess.run(
            adb_prefix + ["shell", "input", "tap", str(x), str(y)], 
            capture_output=True,
            timeout=5,
            check=True
        )
        time.sleep(delay)
    except subprocess.TimeoutExpired:
        logger.error(f"Timeout double tapping at ({x}, {y})")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to double tap at ({x}, {y}): {e.stderr}")
    except Exception as e:
        logger.error(f"Error double tapping: {e}")


def long_press(
    x: int,
    y: int,
    duration_ms: int = 3000,
    device_id: str | None = None,
    delay: float = 1.0,
) -> None:
    """
    Long press at the specified coordinates.

    Args:
        x: X coordinate.
        y: Y coordinate.
        duration_ms: Duration of press in milliseconds.
        device_id: Optional ADB device ID.
        delay: Delay in seconds after long press.
    """
    adb_prefix = _get_adb_prefix(device_id)

    logger.info(f"Long pressing at ({x}, {y}) for {duration_ms}ms")

    try:
        subprocess.run(
            adb_prefix
            + ["shell", "input", "swipe", str(x), str(y), str(x), str(y), str(duration_ms)],
            capture_output=True,
            timeout=5 + duration_ms/1000,
            check=True
        )
        time.sleep(delay)
    except subprocess.TimeoutExpired:
        logger.error(f"Timeout long pressing at ({x}, {y})")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to long press at ({x}, {y}): {e.stderr}")
    except Exception as e:
        logger.error(f"Error long pressing: {e}")


def swipe(
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    duration_ms: int | None = None,
    device_id: str | None = None,
    delay: float = 1.0,
) -> None:
    """
    Swipe from start to end coordinates.

    Args:
        start_x: Starting X coordinate.
        start_y: Starting Y coordinate.
        end_x: Ending X coordinate.
        end_y: Ending Y coordinate.
        duration_ms: Duration of swipe in milliseconds (auto-calculated if None).
        device_id: Optional ADB device ID.
        delay: Delay in seconds after swipe.
    """
    adb_prefix = _get_adb_prefix(device_id)

    if duration_ms is None:
        # Calculate duration based on distance
        dist_sq = (start_x - end_x) ** 2 + (start_y - end_y) ** 2
        duration_ms = int(dist_sq / 1000)
        duration_ms = max(1000, min(duration_ms, 2000))  # Clamp between 1000-2000ms

    logger.info(f"Swiping from ({start_x}, {start_y}) to ({end_x}, {end_y}) in {duration_ms}ms")

    try:
        subprocess.run(
            adb_prefix
            + [
                "shell",
                "input",
                "swipe",
                str(start_x),
                str(start_y),
                str(end_x),
                str(end_y),
                str(duration_ms),
            ],
            capture_output=True,
            timeout=5 + duration_ms/1000,
            check=True
        )
        time.sleep(delay)
    except subprocess.TimeoutExpired:
        logger.error(f"Timeout swiping")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to swipe: {e.stderr}")
    except Exception as e:
        logger.error(f"Error swiping: {e}")


def back(device_id: str | None = None, delay: float = 1.0) -> None:
    """
    Press the back button.

    Args:
        device_id: Optional ADB device ID.
        delay: Delay in seconds after pressing back.
    """
    adb_prefix = _get_adb_prefix(device_id)
    
    logger.info("Pressing Back button")

    try:
        subprocess.run(
            adb_prefix + ["shell", "input", "keyevent", "4"], 
            capture_output=True,
            timeout=5,
            check=True
        )
        time.sleep(delay)
    except subprocess.TimeoutExpired:
        logger.error("Timeout pressing Back")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to press Back: {e.stderr}")
    except Exception as e:
        logger.error(f"Error pressing Back: {e}")


def home(device_id: str | None = None, delay: float = 1.0) -> None:
    """
    Press the home button.

    Args:
        device_id: Optional ADB device ID.
        delay: Delay in seconds after pressing home.
    """
    adb_prefix = _get_adb_prefix(device_id)

    logger.info("Pressing Home button")

    try:
        subprocess.run(
            adb_prefix + ["shell", "input", "keyevent", "KEYCODE_HOME"], 
            capture_output=True,
            timeout=5,
            check=True
        )
        time.sleep(delay)
    except subprocess.TimeoutExpired:
        logger.error("Timeout pressing Home")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to press Home: {e.stderr}")
    except Exception as e:
        logger.error(f"Error pressing Home: {e}")


def launch_app(app_name: str, device_id: str | None = None, delay: float = 1.0) -> bool:
    """
    Launch an app by name.

    Args:
        app_name: The app name (must be in APP_PACKAGES).
        device_id: Optional ADB device ID.
        delay: Delay in seconds after launching.

    Returns:
        True if app was launched, False if app not found.
    """
    if app_name not in APP_PACKAGES:
        logger.warning(f"App not found in configuration: {app_name}")
        return False

    adb_prefix = _get_adb_prefix(device_id)
    package = APP_PACKAGES[app_name]
    
    logger.info(f"Launching app: {app_name} ({package})")

    try:
        subprocess.run(
            adb_prefix
            + [
                "shell",
                "monkey",
                "-p",
                package,
                "-c",
                "android.intent.category.LAUNCHER",
                "1",
            ],
            capture_output=True,
            timeout=10,
            check=True
        )
        time.sleep(delay)
        return True
    except subprocess.TimeoutExpired:
        logger.error(f"Timeout launching app {app_name}")
        return False
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to launch app {app_name}: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Error launching app {app_name}: {e}")
        return False


def _get_adb_prefix(device_id: str | None) -> list:
    """Get ADB command prefix with optional device specifier."""
    if device_id:
        return ["adb", "-s", device_id]
    return ["adb"]


def get_screen_dimensions(device_id: str | None = None) -> Tuple[int, int] | None:
    """
    Get the screen dimensions (width, height) of the device.

    Args:
        device_id: Optional ADB device ID.

    Returns:
        A tuple (width, height) or None if dimensions cannot be determined.
    """
    adb_prefix = _get_adb_prefix(device_id)

    # Try 'wm size' first
    try:
        result = subprocess.run(
            adb_prefix + ["shell", "wm", "size"],
            capture_output=True,
            text=True,
            timeout=5,
            check=True,
        )
        output = result.stdout.strip()
        if "Physical size:" in output:
            size_str = output.split("Physical size:")[1].strip().split("\n")[0]
            width, height = map(int, size_str.split("x"))
            return width, height
        elif "Override size:" in output:
            size_str = output.split("Override size:")[1].strip().split("\n")[0]
            width, height = map(int, size_str.split("x"))
            return width, height
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, ValueError):
        # Fallback to 'dumpsys display' if 'wm size' fails
        pass

    try:
        result = subprocess.run(
            adb_prefix + ["shell", "dumpsys", "display"],
            capture_output=True,
            text=True,
            timeout=5,
            check=True,
        )
        output = result.stdout.strip()
        for line in output.split("\n"):
            if "mBaseDisplayInfo=" in line:
                # Example: mBaseDisplayInfo=DisplayInfo{"Built-in Screen", app 1080 x 1920, ...}
                if "app" in line and "x" in line:
                    parts = line.split("app")[1].split("x")
                    width = int(parts[0].strip())
                    height = int(parts[1].split(",")[0].strip())
                    return width, height
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, ValueError):
        pass

    return None
