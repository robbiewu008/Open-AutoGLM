"""Device control utilities for Android automation."""

import os
import subprocess
import time
from functools import lru_cache
from typing import List, Optional, Tuple

from phone_agent.config.apps import APP_PACKAGES
from phone_agent.log import logger
from phone_agent.utils import retry


@retry(exceptions=(subprocess.CalledProcessError, subprocess.TimeoutExpired))
def get_current_app(device_id: str | None = None) -> str:
    """
    Get the currently focused app name.

    Args:
        device_id: Optional ADB device ID for multi-device setups.

    Returns:
        The app name if recognized, otherwise "System Home".
    """
    adb_prefix = _get_adb_prefix(device_id)

    result = subprocess.run(
        adb_prefix + ["shell", "dumpsys", "window"], 
        capture_output=True, 
        text=True,
        timeout=5,
        check=True
    )
        
    output = result.stdout

    # Parse window focus info
    for line in output.split("\n"):
        if "mCurrentFocus" in line or "mFocusedApp" in line:
            for app_name, package in APP_PACKAGES.items():
                if package in line:
                    return app_name

    return "System Home"


@retry(exceptions=(subprocess.CalledProcessError, subprocess.TimeoutExpired))
def tap(x: int, y: int, device_id: str | None = None, display_id: int = 0, delay: float = 1.0) -> None:
    """
    Tap at the specified coordinates.

    Args:
        x: X coordinate.
        y: Y coordinate.
        device_id: Optional ADB device ID.
        display_id: Display ID to tap on (default: 0).
        delay: Delay in seconds after tap.
    """
    adb_prefix = _get_adb_prefix(device_id)
    
    logger.info(f"Tapping at ({x}, {y}) on device {device_id or 'default'} (display {display_id})")

    subprocess.run(
        adb_prefix + ["shell", "input", "-d", str(display_id), "tap", str(x), str(y)], 
        capture_output=True,
        timeout=5,
        check=True
    )
    time.sleep(delay)


@retry(exceptions=(subprocess.CalledProcessError, subprocess.TimeoutExpired))
def double_tap(
    x: int, y: int, device_id: str | None = None, display_id: int = 0, delay: float = 1.0
) -> None:
    """
    Double tap at the specified coordinates.

    Args:
        x: X coordinate.
        y: Y coordinate.
        device_id: Optional ADB device ID.
        display_id: Display ID to tap on (default: 0).
        delay: Delay in seconds after double tap.
    """
    adb_prefix = _get_adb_prefix(device_id)

    logger.info(f"Double tapping at ({x}, {y}) on device {device_id or 'default'} (display {display_id})")

    subprocess.run(
        adb_prefix + ["shell", "input", "-d", str(display_id), "tap", str(x), str(y)], 
        capture_output=True,
        timeout=5,
        check=True
    )
    time.sleep(0.1)
    subprocess.run(
        adb_prefix + ["shell", "input", "-d", str(display_id), "tap", str(x), str(y)], 
        capture_output=True,
        timeout=5,
        check=True
    )
    time.sleep(delay)


@retry(exceptions=(subprocess.CalledProcessError, subprocess.TimeoutExpired))
def long_press(
    x: int,
    y: int,
    duration_ms: int = 3000,
    device_id: str | None = None,
    display_id: int = 0,
    delay: float = 1.0,
) -> None:
    """
    Long press at the specified coordinates.

    Args:
        x: X coordinate.
        y: Y coordinate.
        duration_ms: Duration of press in milliseconds.
        device_id: Optional ADB device ID.
        display_id: Display ID to tap on (default: 0).
        delay: Delay in seconds after long press.
    """
    adb_prefix = _get_adb_prefix(device_id)

    logger.info(f"Long pressing at ({x}, {y}) for {duration_ms}ms (display {display_id})")

    subprocess.run(
        adb_prefix
        + ["shell", "input", "-d", str(display_id), "swipe", str(x), str(y), str(x), str(y), str(duration_ms)],
        capture_output=True,
        timeout=5 + duration_ms/1000,
        check=True
    )
    time.sleep(delay)


@retry(exceptions=(subprocess.CalledProcessError, subprocess.TimeoutExpired))
def swipe(
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    duration_ms: int | None = None,
    device_id: str | None = None,
    display_id: int = 0,
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
        display_id: Display ID to tap on (default: 0).
        delay: Delay in seconds after swipe.
    """
    adb_prefix = _get_adb_prefix(device_id)

    if duration_ms is None:
        # Calculate duration based on distance
        dist_sq = (start_x - end_x) ** 2 + (start_y - end_y) ** 2
        duration_ms = int(dist_sq / 1000)
        duration_ms = max(1000, min(duration_ms, 2000))  # Clamp between 1000-2000ms

    logger.info(f"Swiping from ({start_x}, {start_y}) to ({end_x}, {end_y}) in {duration_ms}ms (display {display_id})")

    subprocess.run(
        adb_prefix
        + [
            "shell",
            "input",
            "-d", str(display_id),
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


@retry(exceptions=(subprocess.CalledProcessError, subprocess.TimeoutExpired))
def back(device_id: str | None = None, delay: float = 1.0) -> None:
    """
    Press the back button.

    Args:
        device_id: Optional ADB device ID.
        delay: Delay in seconds after pressing back.
    """
    adb_prefix = _get_adb_prefix(device_id)
    
    logger.info("Pressing Back button")

    subprocess.run(
        adb_prefix + ["shell", "input", "keyevent", "4"], 
        capture_output=True,
        timeout=5,
        check=True
    )
    time.sleep(delay)


@retry(exceptions=(subprocess.CalledProcessError, subprocess.TimeoutExpired))
def home(device_id: str | None = None, delay: float = 1.0) -> None:
    """
    Press the home button.

    Args:
        device_id: Optional ADB device ID.
        delay: Delay in seconds after pressing home.
    """
    adb_prefix = _get_adb_prefix(device_id)

    logger.info("Pressing Home button")

    subprocess.run(
        adb_prefix + ["shell", "input", "keyevent", "KEYCODE_HOME"], 
        capture_output=True,
        timeout=5,
        check=True
    )
    time.sleep(delay)


@retry(exceptions=(subprocess.CalledProcessError, subprocess.TimeoutExpired))
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


def _get_adb_prefix(device_id: str | None) -> list:
    """Get ADB command prefix with optional device specifier."""
    if device_id:
        return ["adb", "-s", device_id]
    return ["adb"]


@lru_cache(maxsize=8)
def get_screen_dimensions(device_id: str | None = None) -> Tuple[int, int] | None:
    """
    Get the screen dimensions (width, height) of the device.

    Caches dimensions for up to 8 devices to support multi-device setups
    (e.g., multiple emulators or physical devices in automotive testing).

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
