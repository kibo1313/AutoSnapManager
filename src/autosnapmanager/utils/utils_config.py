import os
import sys

WORK_DIR = os.path.dirname(__file__)
PROJECT_DIR = sys.path[1]


if __name__ == '__main__':
    from autosnapmanager.utils.print_config import print_config

    print_config()
