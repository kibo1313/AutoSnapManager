import os
from adbutils import adb_path

WORK_DIR = os.path.dirname(__file__)

ADB_EXECUTOR = adb_path()

if __name__ == "__main__":
    from utils.print_config import print_config

    print_config()
