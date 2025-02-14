from screencaps.windows.windowcap import WindowCap
from screencaps.windows.fullscreencap import FullScreenCap
from screencaps.android.minicap import MiniCap
from screencaps.android.adbcap import ADBCap

from matches.windows.opencv_match import OpenCVMatch

from actions.clicks.windows.win32api_click import Win32ApiClick
from actions.clicks.windows.win32gui_click import Win32GuiClick
from actions.clicks.windows.pyautogui_click import PyAutoGuiClick
from actions.clicks.android.minitouch import MiniTouch
from actions.clicks.android.adb_touch import ADBTouch

from managers.windows_manager import WindowsManager as Windows
from managers.android_manager import AndroidManager as Android
from managers.manager_config import ScreenCaps, Clicks, Matches

__version__ = "0.1.0"
