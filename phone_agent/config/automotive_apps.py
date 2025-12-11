"""App name to package name mapping for common automotive applications."""

AUTOMOTIVE_APP_PACKAGES: dict[str, str] = {
    # Navigation
    "高德地图车机版": "com.autonavi.amapauto",
    "百度地图车机版": "com.baidu.car.map",
    "地图": "com.google.android.apps.maps", # Generic for Google Maps on AAOS
    "导航": "com.yourcar.navigation", # Placeholder for OEM navigation app

    # Media & Entertainment
    "酷狗音乐车机版": "com.kugou.android.car",
    "QQ音乐车机版": "com.tencent.qqmusiccar",
    "网易云音乐车机版": "com.netease.cloudmusic.car",
    "喜马拉雅车机版": "com.ximalaya.ting.car",
    "收音机": "com.android.car.radio",
    "媒体": "com.android.car.media", # Generic media app

    # Communication
    "蓝牙电话": "com.android.car.dialer",
    "电话": "com.android.car.dialer",
    "信息": "com.android.car.messaging",

    # Vehicle Control & Settings
    "空调": "com.yourcar.hvac", # Placeholder for OEM HVAC app
    "车辆设置": "com.android.car.settings",
    "仪表盘": "com.yourcar.cluster", # Placeholder for OEM cluster app
    "驾驶模式": "com.yourcar.drivingmodes", # Placeholder for OEM driving modes app

    # System & Utilities
    "设置": "com.android.car.settings",
    "应用商店": "com.android.vending", # Google Play Store
    "文件管理": "com.android.documentsui",
    "浏览器": "com.android.chrome", # Chrome browser
}

def get_automotive_package_name(app_name: str) -> str | None:
    """
    Get the package name for an automotive app.

    Args:
        app_name: The display name of the automotive app.

    Returns:
        The Android package name, or None if not found.
    """
    return AUTOMOTIVE_APP_PACKAGES.get(app_name)

def get_automotive_app_name(package_name: str) -> str | None:
    """
    Get the app name from an automotive package name.

    Args:
        package_name: The Android package name.

    Returns:
        The display name of the app, or None if not found.
    """
    for name, package in AUTOMOTIVE_APP_PACKAGES.items():
        if package == package_name:
            return name
    return None

def list_supported_automotive_apps() -> list[str]:
    """
    Get a list of all supported automotive app names.

    Returns:
        List of app names.
    """
    return list(AUTOMOTIVE_APP_PACKAGES.keys())
