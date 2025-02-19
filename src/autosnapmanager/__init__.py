from .actions.clicks.android.adb_touch import ADBTouch
from .actions.clicks.android.minitouch import MiniTouch
from .actions.clicks.android.maatouch import MAATouch
from .actions.clicks.windows.pyautogui_click import PyAutoGuiClick
from .actions.clicks.windows.win32api_click import Win32ApiClick
from .actions.clicks.windows.win32gui_click import Win32GuiClick
from .managers.android_manager import AndroidManager as Android
from .managers.manager_config import ScreenCaps, Clicks, Matches
from .managers.windows_manager import WindowsManager as Windows
from .matches.windows.opencv_match import OpenCVMatch
from .screencaps.android.adbcap import ADBCap
from .screencaps.android.minicap import MiniCap
from .screencaps.windows.fullscreencap import FullScreenCap
from .screencaps.windows.windowcap import WindowCap

__all__ = [
    'ADBTouch', 'MiniTouch', 'MAATouch',
    'PyAutoGuiClick', 'Win32ApiClick', 'Win32GuiClick',
    'Android', 'Windows',
    'ScreenCaps', 'Clicks', 'Matches',
    'OpenCVMatch',
    'ADBCap', 'MiniCap', 'FullScreenCap', 'WindowCap',
    '__version__'
]

__version__ = "0.1.1"
