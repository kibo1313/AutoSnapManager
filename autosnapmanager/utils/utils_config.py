import os

WORK_DIR = os.path.dirname(__file__)
PROJECT_DIR = os.path.dirname(os.path.dirname(WORK_DIR))  # sys.path[1]


if __name__ == '__main__':
    from utils.print_config import print_config

    print_config()
