"""
Android 设备触摸操作实现
使用 minitouch 实现多点触控操作
"""

import socket
import subprocess
from time import sleep
from typing import Optional, Tuple, List

from adbutils import adb

from autosnapmanager.actions.clicks.android.touch import Touch
from autosnapmanager.actions.clicks.android.touch_config import (
    ADB_EXE, MINITOUCH_PATH, MINITOUCH_REMOTE_PATH,
    MINITOUCH_REMOTE_ADDR, MINITOUCH_SERVER_START_DELAY,
    DEFAULT_HOST
)
from autosnapmanager.utils.adb_devices import DeviceInfo
from autosnapmanager.utils.command_builder_utils import CommandBuilder
from autosnapmanager.utils.logger import logger


class MiniTouchError(Exception):
    """MiniTouch 相关错误的基类"""
    pass


class MiniTouchUnSupportError(MiniTouchError):
    """设备不支持 MiniTouch"""
    pass


class MiniTouchManager:
    """MiniTouch 服务管理者"""

    ROTATION_MAP = {
        0: lambda x, y, w, h: (x, y),
        1: lambda x, y, w, h: (h - y, x),
        2: lambda x, y, w, h: (w - x, h - y),
        3: lambda x, y, w, h: (y, w - x)
    }

    def __init__(self, serial: str):
        """
        初始化 MiniTouch 管理器
        
        Args:
            serial: 设备序列号
            
        Raises:
            MiniTouchUnSupportError: 当设备不支持 MiniTouch 时抛出
        """
        self._adb = adb.device(serial)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._process: Optional[subprocess.Popen] = None
        self._mapped_port: Optional[int] = None  # 映射到本机的端口
        self.device_info = self._get_device_info()

        try:
            self._init_minitouch()
            self.start_minitouch_service()
        except Exception as e:
            logger.error(f"MiniTouch 初始化失败: {e}")
            self.stop_minitouch_service()
            raise

    def _get_device_info(self) -> DeviceInfo:
        """
        获取设备信息

        Returns:
            DeviceInfo: 包含设备信息的对象
        """
        window_size = self._adb.window_size()
        return DeviceInfo(
            abi=self._adb.getprop("ro.product.cpu.abi"),
            sdk=self._adb.getprop("ro.build.version.sdk"),
            width=window_size.width,
            height=window_size.height,
            rotation=self._adb.rotation()
        )

    def _init_minitouch(self) -> None:
        """初始化 MiniTouch 服务"""
        self._kill_minitouch_process()
        self._setup_minitouch()

    def start_minitouch_service(self) -> None:
        """启动 MiniTouch 服务"""
        self._start_minitouch_process()
        self._setup_port_forwarding()
        self._create_socket()
        self._read_socket_info()

    def stop_minitouch_service(self) -> None:
        """停止 MiniTouch 服务并清理资源"""
        try:
            self._close_socket()
            if self._process and self._process.poll() is None:
                self._process.kill()
                self._process = None

            logger.debug("MiniTouch 资源清理完成")
        except Exception as e:
            logger.error(f"MiniTouch 资源清理过程中出错: {e}")
            raise

    def _kill_minitouch_process(self) -> None:
        """终止设备上的 MiniTouch 进程"""
        try:
            self._adb.shell(["pkill", "-9", "minitouch"])
        except Exception as e:
            logger.warning(f"终止 MiniTouch 进程失败 {e}")

    def _setup_minitouch(self) -> None:
        """安装 MiniTouch 到设备"""
        try:
            self._adb.sync.push(
                f"{MINITOUCH_PATH}/{self.device_info.abi}/minitouch",
                MINITOUCH_REMOTE_PATH
            )
            self._adb.shell(f"chmod +x {MINITOUCH_REMOTE_PATH}")
        except Exception as e:
            logger.error(f"MiniTouch 安装失败: {e}")
            raise

    def _start_minitouch_process(self) -> None:
        """启动 MiniTouch 进程"""
        try:
            cmd = [ADB_EXE]
            if self._adb.serial:
                cmd.extend(["-s", self._adb.serial])
            cmd.extend(["shell", MINITOUCH_REMOTE_PATH])

            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            sleep(MINITOUCH_SERVER_START_DELAY)
            logger.info(f"MiniTouch 进程已启动: {' '.join(cmd)}")
        except Exception as e:
            logger.error(f"MiniTouch 进程启动失败: {e}")
            raise

    def _setup_port_forwarding(self) -> None:
        """设置端口转发"""
        try:
            self._mapped_port = self._adb.forward_port(MINITOUCH_REMOTE_ADDR)
            logger.info(f"端口转发设置完成: {self._mapped_port}")
        except Exception as e:
            logger.error(f"MiniTouch 端口转发失败: {e}")
            raise

    def _create_socket(self) -> None:
        """建立 Socket 连接"""
        try:
            self.sock.settimeout(10)
            self.sock.connect((DEFAULT_HOST, self._mapped_port))
        except Exception as e:
            logger.error(f"Minitouch Socket 连接失败: {e}")
            raise

    def _read_socket_info(self) -> None:
        """读取 Socket 连接信息"""
        try:
            with self.sock.makefile() as sock_file:
                # v <version>
                version = sock_file.readline().strip()
                # ^ <max-contacts> <max-x> <max-y> <max-pressure>
                _, max_contacts, max_x, max_y, max_pressure = sock_file.readline().strip().split()
                # $ <pid>
                _, pid = sock_file.readline().strip().split()

                logger.info(f"MiniTouch 服务信息: PID={pid}, 版本={version}")
                logger.info(f"最大触点={max_contacts}, X={max_x}, Y={max_y}, 压力值={max_pressure}")
        except Exception as e:
            logger.error(f"读取 MiniTouch 设备信息失败: {e}")
            raise

    def _close_socket(self) -> None:
        """关闭 Socket 连接"""
        try:
            if self.sock:
                self.sock.close()
                logger.info("MiniTouch Socket 连接已关闭")
        except Exception as e:
            logger.error(f"关闭MiniTouch Socket 连接失败: {e}")
            raise

    def __del__(self):
        """析构时自动清理资源"""
        self.stop_minitouch_service()


class MiniTouch(Touch):
    """MiniTouch 触摸操作实现"""

    def __init__(self, serial: str):
        """
        初始化 MiniTouch 操作对象
        
        Args:
            serial: 设备序列号
        """
        self.minitouch = MiniTouchManager(serial)
        self._builder = CommandBuilder(self.minitouch.sock)

    def click(self, x: int, y: int, duration: int = 50) -> None:
        """
        执行点击操作
        
        Args:
            x: 点击横坐标
            y: 点击纵坐标
            duration: 点击持续时间(ms)
        """
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
        start_x, start_y = self._convert_coordinates(start_x, start_y)
        end_x, end_y = self._convert_coordinates(end_x, end_y)
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
        converted_points = [self._convert_coordinates(x, y) for x, y in points]

        # 按下所有触点
        for point_id, (x, y) in enumerate(converted_points):
            self._builder.down(point_id, x, y, pressure)
        self._builder.publish()

        if duration:
            self._builder.waitTo(duration)

        if up:
            for point_id in range(len(converted_points)):
                self._builder.upTo(point_id)

    def _convert_coordinates(self, x: int, y: int) -> Tuple[int, int]:
        """
        根据设备旋转转换坐标
        
        Args:
            x: 原始横坐标
            y: 原始纵坐标
            
        Returns:
            转换后的坐标元组
        """
        rotation = self.minitouch.device_info.rotation
        width = self.minitouch.device_info.width
        height = self.minitouch.device_info.height
        return self.minitouch.ROTATION_MAP[rotation](x, y, width, height)


if __name__ == "__main__":
    # 示例用法
    touch = MiniTouch("127.0.0.1:16384")
    try:
        touch.swipe(100, 800, 800, 800)
        # sleep(0.5)
        # touch.swipe(800, 800, 100, 800)
    finally:
        touch.minitouch.stop_minitouch_service()
