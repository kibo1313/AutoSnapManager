import os
from adbutils import adb_path

WORK_DIR = os.path.dirname(__file__)

# adb
ADB_EXE = adb_path()

# connection
DEFAULT_HOST = "127.0.0.1"
DEFAULT_CHARSET = "utf-8"
DEFAULT_BUFFER_SIZE = 0

# MiniTouch
MINITOUCH_PATH = rf"{WORK_DIR}\bin\minitouch\libs"
MINITOUCH_REMOTE_PATH = "/data/local/tmp/minitouch"
MINITOUCH_REMOTE_ADDR = "localabstract:minitouch"
MINITOUCH_SERVER_START_DELAY = 1

# MaaTouch
MAATOUCH_PATH = rf"{WORK_DIR}\bin\maatouch"
MAATOUCH_REMOTE_PATH = "/data/local/tmp/maatouch"
MAA_PACKAGE_NAME = "com.shxyke.MaaTouch.App"
MAATOUCH_SERVER_START_DELAY = 1

# operation
DEFAULT_DELAY = 0.05


if __name__ == "__main__":
    from utils.print_config import print_config

    print_config()
