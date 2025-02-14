import socket
from time import sleep
from typing import Optional, List, Tuple

from adbutils import adb

from actions.clicks.android.touch import Touch
from actions.clicks.android.touch_config import (
    MAATOUCH_PATH, MAATOUCH_REMOTE_PATH,
    MAA_PACKAGE_NAME, MAATOUCH_SERVER_START_DELAY
)
from utils.command_builder_utils import CommandBuilder
from utils.logger import logger


class MAATouchError(Exception):
    pass


class MAATouchUnSupportError(MAATouchError):
    pass


class MAATouchManager:
    """https://github.com/MaaAssistantArknights/MaaTouch"""

    def __init__(self, serial: str):
        self._adb = adb.device(serial)
        self.sock: Optional[socket.socket] = None

        try:
            self._setup_maatouch()
            self.start_maatouch_service()
        except Exception as e:
            logger.error(f"MAATouch 初始化失败: {e}")
            self.stop_maatouch_service()
            raise

    def _setup_maatouch(self) -> None:
        """安装 MAATouch 到设备"""
        try:
            self._adb.sync.push(MAATOUCH_PATH, MAATOUCH_REMOTE_PATH)
        except Exception as e:
            logger.error(f"MiniTouch 安装失败: {e}")
            raise

    def start_maatouch_service(self) -> None:
        """启动 MAATouch 服务"""
        self._start_maatouch_process()
        self._create_socket()

    def stop_maatouch_service(self) -> None:
        """停止 MAATouch 服务并清理资源"""
        try:
            self._close_socket()
            self._process.close()

            logger.debug("MiniTouch 资源清理完成")
        except Exception as e:
            logger.error(f"MiniTouch 资源清理过程中出错: {e}")
            raise

    def _start_maatouch_process(self) -> None:
        """启动 MAATouch 进程"""
        try:
            cmd = f"CLASSPATH={MAATOUCH_REMOTE_PATH} app_process / {MAA_PACKAGE_NAME}"
            self._process = self._adb.shell(cmd, stream=True)
            sleep(MAATOUCH_SERVER_START_DELAY)
            logger.info(f"MAATouch 进程已启动: adb shell {cmd}")
        except Exception as e:
            logger.error(f"MAATouch 启动失败: {e}")
            raise

    def _create_socket(self) -> None:
        """建立 Socket 连接"""
        try:
            self.sock = self._process.conn
            self.sock.settimeout(10)
            self._read_socket_info()
        except Exception as e:
            logger.error(f"MAATouch Socket 连接失败: {e}")
            raise

    def _read_socket_info(self) -> None:
        """读取 Socket 连接信息"""
        try:
            with self.sock.makefile() as sock_file:
                # ^ <max-contacts> <max-x> <max-y> <max-pressure>
                _, max_contacts, max_x, max_y, max_pressure = sock_file.readline().strip().split()

                logger.info(f"MAATouch 服务信息: 最大触点={max_contacts}, X={max_x}, Y={max_y}, 压力值={max_pressure}")
        except Exception as e:
            logger.error(f"读取 MAATouch 设备信息失败: {e}")
            raise

    def _close_socket(self) -> None:
        """关闭 Socket 连接"""
        try:
            if self.sock:
                self.sock.close()
                logger.info("Socket 连接已关闭")
        except Exception as e:
            logger.error(f"关闭AATouch Socket 连接失败: {e}")
            raise

    def __del__(self):
        """析构时自动清理资源"""
        self.stop_maatouch_service()


class MAATouch(Touch):
    def __init__(self, serial: str):
        """
        初始化 MiniTouch 操作对象

        Args:
            serial: 设备序列号
        """
        self.maatouch = MAATouchManager(serial)
        self._builder = CommandBuilder(self.maatouch.sock)

    def click(self, x: int, y: int, duration: int = 50) -> None:
        self._tap([(x, y)], duration=duration)

    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int) -> None:
        """
        执行滑动操作

        Args:
            start_x: 起始横坐标
            start_y: 起始纵坐标
            end_x: 结束横坐标
            end_y: 结束纵坐标
        """
        mid_x, mid_y = (start_x + end_x) // 2, (start_y + end_y) // 2

        self._builder.downTo(0, start_x, start_y, 50)
        self._builder.moveTo(0, mid_x, mid_y, 50)
        self._builder.moveTo(0, end_x, end_y, 50)
        self._builder.upTo(0)
        # Todo: random swipe(The more movement actions there are, the slower the movement speed.)

    def _tap(self, points: List[Tuple[int, int]],
             pressure: int = 50, duration: Optional[int] = None,
             up: bool = True) -> None:
        """
        执行多点触控操作

        Args:
            points: 触点坐标列表，如 [(x1， y1), (x2， y2)]
            pressure: 触摸压力值
            duration: 按压持续时间 (ms)
            up: 是否抬起触点
        """
        # 按下所有触点
        for point_id, (x, y) in enumerate(points):
            self._builder.down(point_id, x, y, pressure)
        self._builder.publish()

        if duration:
            self._builder.waitTo(duration)

        if up:
            for point_id in range(len(points)):
                self._builder.upTo(point_id)


if __name__ == "__main__":
    touch = MAATouch("127.0.0.1:16384")
    try:
        touch.click(200, 150)
        # touch.swipe(100, 800, 800, 800)
        # sleep(0.5)
        # touch.swipe(800, 800, 100, 800)
    finally:
        touch.maatouch.stop_maatouch_service()
