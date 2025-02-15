import os

WORK_DIR = os.path.dirname(__file__)

if __name__ == "__main__":
    from autosnapmanager.utils.print_config import print_config

    print_config()
