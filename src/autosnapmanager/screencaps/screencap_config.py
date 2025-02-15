import os
from adbutils import adb_path
from datetime import datetime

WORK_DIR = os.path.dirname(__file__)

NOW_TIME = datetime.now().strftime('%Y-%m-%d_%H_%M_%S')

# adb
ADB_EXE = adb_path()

# connection
DEFAULT_HOST = "127.0.0.1"
PORT_SET = set(range(20000, 21000))

# operation
DEFAULT_BUFFER_SIZE = 1024

# MINICAP
MINICAP_PATH = rf"{WORK_DIR}\android\bin\minicap\libs"
MINICAPSO_PATH = rf"{WORK_DIR}\android\bin\minicap\jni"
MINICAP_REMOTE_HOME = "/data/local/tmp/minicap"
MINICAPSO_REMOTE_HOME = "/data/local/tmp/minicap.so"
MINITOUCH_REMOTE_ADDR = "localabstract:minicap"
MINICAP_SERVER_START_DELAY = 3
MINICAP_COMMAND = [
    "LD_LIBRARY_PATH=/data/local/tmp",
    "/data/local/tmp/minicap"
]

if __name__ == "__main__":
    from autosnapmanager.utils.print_config import print_config

    print_config()
