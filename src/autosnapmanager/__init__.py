from autosnapmanager.actions.clicks.android.adb_touch import ADBTouch
from autosnapmanager.actions.clicks.android.minitouch import MiniTouch
from autosnapmanager.actions.clicks.windows.pyautogui_click import PyAutoGuiClick
from autosnapmanager.actions.clicks.windows.win32api_click import Win32ApiClick
from autosnapmanager.actions.clicks.windows.win32gui_click import Win32GuiClick
from autosnapmanager.managers.android_manager import AndroidManager as Android
from autosnapmanager.managers.manager_config import ScreenCaps, Clicks, Matches
from autosnapmanager.managers.windows_manager import WindowsManager as Windows
from autosnapmanager.matches.windows.opencv_match import OpenCVMatch
from autosnapmanager.screencaps.android.adbcap import ADBCap
from autosnapmanager.screencaps.android.minicap import MiniCap
from autosnapmanager.screencaps.windows.fullscreencap import FullScreenCap
from autosnapmanager.screencaps.windows.windowcap import WindowCap

__version__ = "0.1.0"
