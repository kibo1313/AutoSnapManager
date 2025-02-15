from enum import Enum


class StrEnum(str, Enum):
    pass


class System(StrEnum):
    Windows = 'windows'
    Android = 'android'
    Mac = 'mac'
    Linux = 'linux'


class ScreenCaps(StrEnum):
    FullScreen = 'fullscreen'
    Window = 'window'
    Adb = 'adb'
    MiniCap = 'minicap'


class Matches(StrEnum):
    OpenCV = 'opencv'


class Clicks(StrEnum):
    PyAutoGui = 'pyautogui'
    Win32Api = 'win32api'
    Win32Gui = 'win32gui'
    Adb = 'adb'
    MiniTouch = 'minitouch'
    MAATouch = 'maatouch'


PARAMS_MAP = {
    System.Windows: ["window_name"],
    System.Android: ["serial"],
}

MANAGER = {
    System.Windows: 'autosnapmanager.managers.windows_manager.WindowsManager',
    System.Android: 'autosnapmanager.managers.android_manager.AndroidManager',
}

SCREENCAP = {
    System.Windows: {
        'fullscreen': 'autosnapmanager.screencaps.windows.fullscreencap.FullScreenCap',
        'window': 'autosnapmanager.screencaps.windows.windowcap.WindowCap',
    },
    System.Android: {
        'adb': 'autosnapmanager.screencaps.android.adbcap.ADBCap',
        'minicap': 'autosnapmanager.screencaps.android.minicap.MiniCap',
    },
}

MATCH = {
    System.Windows: {
        'opencv': 'autosnapmanager.matches.windows.opencv_match.OpenCVMatch',
    },
    System.Android: {
        'opencv': 'autosnapmanager.matches.android.opencv_match.OpenCVMatch',
    },
}

CLICK = {
    System.Windows: {
        'pyautogui': 'autosnapmanager.actions.clicks.windows.pyautogui_click.PyAutoGuiClick',
        'win32api': 'autosnapmanager.actions.clicks.windows.win32api_click.Win32ApiClick',
        'win32gui': 'autosnapmanager.actions.clicks.windows.win32gui_click.Win32GuiClick',
    },
    System.Android: {
        'adb': 'autosnapmanager.actions.clicks.android.adb_touch.ADBTouch',
        'minitouch': 'autosnapmanager.actions.clicks.android.minitouch.MiniTouch',
        'maatouch': 'autosnapmanager.actions.clicks.android.maatouch.MAATouch',
    },
}

CLASSMAP = {
    'Manager': MANAGER,
    'ScreenCap': SCREENCAP,
    'Match': MATCH,
    'Click': CLICK,
    'Touch': CLICK,
}

DefaultMethods = {
    'ScreenCap': {
        System.Windows: ('window', 'fullscreen'),
        System.Android: ('minicap', 'minicap'),
    },
    'Match': {
        System.Windows: ('opencv', 'opencv'),
        System.Android: ('opencv', 'opencv'),
    },
    'Click': {
        System.Windows: ('win32gui', 'pyautogui'),
        System.Android: ('adb', 'adb'),
    },
}

DefaultArgs = {
    System.Windows: {'window_name'},
    System.Android: {'serial'},
}

if __name__ == '__main__':
    from autosnapmanager.utils.print_config import print_config

    print_config()
