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
    ADB = 'adb'
    MiniTouch = 'minitouch'
    MAATouch = 'maatouch'


PARAMS_MAP = {
    System.Windows: ["window_name"],
    System.Android: ["serial"],
}

MANAGER = {
    System.Windows: 'managers.windows_manager.WindowsManager',
    System.Android: 'managers.android_manager.AndroidManager',
}

SCREENCAP = {
    System.Windows: {
        'fullscreen': 'screencaps.windows.fullscreencap.FullScreenCap',
        'window': 'screencaps.windows.windowcap.WindowCap',
    },
    System.Android: {
        'adb': 'screencaps.android.adbcap.ADBCap',
        'minicap': 'screencaps.android.minicap.MiniCap',
    },
}

MATCH = {
    System.Windows: {
        'opencv': 'matches.windows.opencv_match.OpenCVMatch',
    },
    System.Android: {
        'opencv': 'matches.android.opencv_match.OpenCVMatch',
    },
}

CLICK = {
    System.Windows: {
        'pyautogui': 'actions.clicks.windows.pyautogui_click.PyAutoGuiClick',
        'win32api': 'actions.clicks.windows.win32api_click.Win32ApiClick',
        'win32gui': 'actions.clicks.windows.win32gui_click.Win32GuiClick',
    },
    System.Android: {
        'adb': 'actions.clicks.android.adb_touch.ADBTouch',
        'minitouch': 'actions.clicks.android.minitouch.MiniTouch',
        'maatouch': 'actions.clicks.android.maatouch.MAATouch',
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
        System.Android: ('minicap',),
    },
    'Match': {
        System.Windows: ('opencv', 'opencv'),
        System.Android: ('opencv',),
    },
    'Click': {
        System.Windows: ('win32gui', 'pyautogui'),
    },
    'Touch': {
        System.Android: ('adb',),
    }

}

if __name__ == '__main__':
    from utils.print_config import print_config

    print_config()
