import io
import json
import socket
import struct
import subprocess
import threading
from queue import Queue, Empty
from time import sleep
from typing import Optional, Dict, Tuple

import numpy as np
from PIL import Image
from adbutils import adb

from screencaps.screencap import ScreenCap
from screencaps.screencap_config import (
    DEFAULT_HOST, ADB_EXE, MINICAP_PATH, MINICAPSO_PATH,
    MINICAP_REMOTE_HOME, MINICAPSO_REMOTE_HOME, MINITOUCH_REMOTE_ADDR,
    MINICAP_COMMAND, MINICAP_SERVER_START_DELAY, DEFAULT_BUFFER_SIZE
)
from utils.adb_devices import DeviceInfo
from utils.logger import logger


class MiniCapError(Exception):
    """MiniCap 相关错误的基类"""
    pass


class StreamHandleError(MiniCapError):
    """流处理异常"""
    pass


class MiniCapUnSupportError(MiniCapError):
    """设备不支持 MiniCap"""
    pass


class MiniCapManager:
    def __init__(
            self,
            serial: str,
            rate: Optional[int] = None,
            quality: int = 100,
            timeout: Optional[int] = None,
            host: str = DEFAULT_HOST,
            skip_frame: bool = True,
            use_stream: bool = True
    ):
        """
        初始化 MiniCap 对象

        Args:
            serial: 设备序列号
            rate: 截图帧率，None表示自动
            quality: 图像质量(1-100)
            timeout: 超时时间(ms)
            host: 连接地址（默认：127.0.0.1）
            skip_frame: 当处理帧的速度跟不上捕获速度时,是否跳过它们
            use_stream: 是否使用流模式
        """
        self._adb = adb.device(serial)
        self.config: [Optional[int], int, Optional[int], str, int, bool, bool] = {
            'rate': rate,
            'quality': quality,
            'timeout': timeout,
            'host': host,
            'mapped_port': 0,
            'skip_frame': skip_frame,
            'use_stream': use_stream,
        }

        self.stream: Optional[MiniCapStream] = None
        self._process: Optional[subprocess.Popen] = None

        try:
            # 初始化设备信息和MiniCap服务
            self.device_info = self._get_device_base_info()
            self.init_minicap()
            self.device_info = self._init_device()
            self.start_minicap_service() if self.config['use_stream'] else None
        except Exception as e:
            logger.error(f"MiniCap初始化失败: {e}")
            self.stop_minicap_service()
            raise

    def init_minicap(self) -> None:
        """初始化 MiniCap 服务"""
        self._kill_minicap_process()
        self._setup_minicap()

    def start_minicap_service(self) -> None:
        """启动 MiniCap 服务"""
        self._start_minicap_process()
        self._setup_port_forwarding()
        self._init_stream()

    def stop_minicap_service(self) -> None:
        """停止 MiniCap 服务 并清理 MiniCap 相关资源"""
        try:
            if self.stream:
                self.stream.stop()
                self.stream = None

            if self._process and self._process.poll() is None:
                self._process.kill()
                self._process = None

            logger.debug("MiniCap 资源清理完成")
        except Exception as e:
            logger.error(f"MiniCap 资源清理过程中出错: {e}")
            raise

    def capture_frame(self) -> bytes:
        """
        捕获单帧图像

        Returns:
            bytes: JPEG格式的图像数据

        Raises:
            RuntimeError: 当捕获失败时抛出
        """
        try:
            adb_command = MINICAP_COMMAND + [
                "-P", f"{self.device_info.vm_size}@{self.device_info.vm_size}/{self.device_info.rotation}",
                "-Q", str(self.config['quality']),
                "-s"
            ]
            raw_data = self._adb.shell(adb_command, encoding=None)
            return raw_data.split(b"for JPG encoder\n")[-1]
        except Exception as e:
            logger.error(f"帧捕获失败: {e}")
            raise

    def _get_device_base_info(self) -> DeviceInfo:
        """获取基础信息"""
        abi = self._adb.getprop("ro.product.cpu.abi")
        sdk = self._adb.getprop("ro.build.version.sdk")

        # 特殊情况处理
        if sdk == "32" and abi == "x86_64":
            abi = "x86"
        if int(sdk) > 34:
            raise MiniCapUnSupportError("不支持 Android 12+")

        return DeviceInfo(
            abi=abi,
            sdk=sdk
        )

    def _get_device_detail_info(self) -> Dict:
        """
        获取设备输入信息

        Returns:
            Dict: 设备信息字典

        Raises:
            MiniCapUnSupportError: 当获取信息失败时抛出
        """
        try:
            info_result = self._adb.shell(MINICAP_COMMAND + ["-i"])
            start_index = info_result.find('{')

            if start_index == -1:
                raise MiniCapUnSupportError("无法获取设备信息")

            info = info_result[start_index:]
            logger.info(f"设备信息: {info}")
            return json.loads(info)

        except Exception as e:
            logger.error(f"获取设备信息失败: {e}")
            raise

    def _init_device(self) -> DeviceInfo:
        """
        初始化设备信息

        Returns:
            DeviceInfo: 设备信息对象

        Raises:
            MiniCapUnSupportError: 当设备不支持时抛出
        """
        try:
            info = self._get_device_detail_info()

            return DeviceInfo(
                id=info.get("id"),
                width=info.get("width"),
                height=info.get("height"),
                size=info.get("size"),
                density=info.get("density"),
                fps=info.get("fps") if self.config['rate'] is None else self.config['rate'],
                rotation=info.get("rotation")
            )
        except Exception as e:
            logger.error(f"设备初始化失败: {e}")
            raise

    def _kill_minicap_process(self) -> None:
        """终止设备上运行的 minicap 进程"""
        try:
            self._adb.shell(["pkill", "-9", "minicap"])
        except Exception as e:
            logger.warning(f"终止 MiniCap 进程失败: {e}")
            raise

    def _setup_minicap(self) -> None:
        """
        安装 minicap 到设备

        Raises:
            RuntimeError: 安装失败时抛出
        """
        try:
            self._adb.sync.push(
                f"{MINICAP_PATH}/{self.device_info.abi}/minicap",
                MINICAP_REMOTE_HOME
            )

            self._adb.sync.push(
                f"{MINICAPSO_PATH}/android-{self.device_info.sdk}/{self.device_info.abi}/minicap.so",
                MINICAPSO_REMOTE_HOME
            )

            self._adb.shell(["chmod", "+x", MINICAP_REMOTE_HOME])

        except Exception as e:
            logger.error(f"MiniCap 安装失败: {e}")
            raise

    def _start_minicap_process(self) -> None:
        """
        启动 minicap 服务进程

        Raises:
            RuntimeError: 启动失败时抛出
        """
        try:
            adb_command = [ADB_EXE]
            if self._adb.serial:
                adb_command.extend(["-s", self._adb.serial])

            adb_command.extend([
                "shell",
                *MINICAP_COMMAND,
                "-P", f"{self.device_info.vm_size}@{self.device_info.vm_size}/{self.device_info.rotation}",
                "-Q", str(self.config['quality']),
                "-r", str(self.device_info.fps)
            ])

            if self.config['skip_frame']:
                adb_command.append("-S")

            logger.info(f"MiniCap 进程已启动: {' '.join(adb_command)}")

            self._process = subprocess.Popen(
                adb_command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            for i in range(MINICAP_SERVER_START_DELAY):
                logger.info(f"MiniCap启动中: {MINICAP_SERVER_START_DELAY - i}秒")
                sleep(1)

        except Exception as e:
            logger.error(f"MiniCap 服务启动失败: {e}")
            raise

    def _setup_port_forwarding(self) -> None:
        """
        设置端口转发

        Raises:
            RuntimeError: 端口转发失败时抛出
        """
        try:
            self.config['mapped_port']: int = self._adb.forward_port(MINITOUCH_REMOTE_ADDR)
        except Exception as e:
            logger.error(f"MiniCap 端口转发设置失败: {e}")
            raise

    def _init_stream(self) -> None:
        """
        初始化并启动数据流读取

        Raises:
            RuntimeError: 数据流初始化失败时抛出
        """
        try:
            self.stream = MiniCapStream(
                self.config['host'],
                self.config['mapped_port'],
                self.config['timeout']
            )
            self.stream.start()
        except Exception as e:
            logger.error(f"MiniCap 数据流初始化失败: {e}")
            raise

    def __del__(self) -> None:
        """析构时确保资源被清理"""
        self.stop_minicap_service()


class MiniCapStream:
    """MiniCap 数据流处理类"""

    __slots__ = ('host', 'port', 'timeout', 'sock', 'data', 'cache', 'lock', 'stop_event', 'thread')

    def __init__(self, host: str, port: int, timeout: Optional[int] = None):
        self.host = host
        self.port = port
        self.timeout = timeout  # ms
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.data = Queue(maxsize=1)  # 存储图像数据的队列(只保留最新数据）
        self.cache: bytes = b''  # 缓存帧
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._read_stream, daemon=True)

    def start(self) -> None:
        """启动数据流处理"""
        try:
            self._create_socket()
            self.thread.start()
            logger.info("数据流已启动")
        except Exception as e:
            logger.error(f"数据流启动失败: {e}")
            self._close_socket()
            raise

    def stop(self) -> None:
        """停止数据流处理"""
        logger.info("正在停止数据流")
        self.stop_event.set()
        self.thread.join()
        self._close_socket()

    def capture_frame(self, use_cache: bool = True) -> bytes:
        """
        捕获一帧数据
        
        Args:
            use_cache: 捕获超时时是否使用缓存帧
        Returns:
            bytes: JPEG 图像数据
        """
        with self.lock:
            self.cache = self.data.get()

        try:
            with self.lock:
                timeout = self.timeout / 1000 if self.timeout and use_cache else None
                return self.data.get(timeout=timeout)
        except Empty:
            logger.debug("获取超时，返回缓存帧")
            return self.cache

    def _create_socket(self) -> bool:
        """连接到指定主机和端口"""
        try:
            self.sock.settimeout(10)
            self.sock.connect((self.host, self.port))
            logger.info(f"已连接到 {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"MiniCap 主机端口连接失败: {e}")
            raise

    def _close_socket(self) -> None:
        """关闭socket连接"""
        try:
            self.sock.close()
            logger.info("MiniCap Socket已关闭")
        except Exception as e:
            logger.error(f"关闭MiniCap Socket失败: {e}")
            raise

    def _read_stream(self) -> None:
        """读取数据流"""
        banner = {}  # 24bytes(1+1+(4*5)+1+1)
        state = "banner"
        expected_size = 2  # 初始读取version和length
        buffer = bytearray()
        frame_body_length = remaining_bytes = 0  # 帧体长度与剩余需读取字节数

        while not self.stop_event.is_set():
            try:
                # (24, 1024, ...)
                chunk = self.sock.recv(remaining_bytes or DEFAULT_BUFFER_SIZE)
                if not chunk:
                    break

                buffer.extend(chunk)
                cursor = 0

                while cursor < len(buffer):
                    if state == "banner" and len(buffer) >= cursor + expected_size:
                        banner, state = self._read_banner(buffer, cursor)
                        cursor += 2

                    elif state == "banner_rest" and len(buffer) >= cursor + expected_size:
                        banner_rest, state, expected_size = self._read_banner_rest(buffer, cursor)
                        banner.update(banner_rest)
                        logger.info(f"banner {banner}")
                        buffer.clear()
                        break

                    elif state == "frame_header" and len(buffer) >= cursor + expected_size:
                        frame_body_length, state = self._read_frame_header(buffer, cursor)
                        cursor += 4

                    elif state == "frame_body" and len(buffer) >= cursor + frame_body_length:
                        frame_body = self._read_frame_body(buffer, cursor, frame_body_length)

                        while not self.data.empty():
                            self.data.get_nowait()
                        self.data.put_nowait(frame_body)

                        state = "frame_header"
                        frame_body_length = remaining_bytes = 0
                        buffer.clear()
                        break

                    else:
                        buffer = buffer[cursor:]
                        remaining_bytes = frame_body_length - len(buffer)
                        break

            except Exception as e:
                logger.error(f"读取数据流错误: {e}")
                break

    @staticmethod
    def _read_banner(buffer: bytearray, cursor: int) -> Tuple[Dict, str]:
        """读取banner信息"""
        version, length = struct.unpack_from('BB', buffer, cursor)
        banner = {'version': version, 'length': length}
        return banner, "banner_rest"

    @staticmethod
    def _read_banner_rest(buffer: bytearray, cursor: int) -> Tuple[Dict, str, int]:
        """读取剩余banner信息"""
        fmt = '<IIIIIBB'
        fields = struct.unpack_from(fmt, buffer, cursor)
        return {
            'pid': fields[0],
            'realWidth': fields[1],
            'realHeight': fields[2],
            'virtualWidth': fields[3],
            'virtualHeight': fields[4],
            'orientation': fields[5] * 90,
            'quirks': fields[6]
        }, "frame_header", 4

    @staticmethod
    def _read_frame_header(buffer: bytearray, cursor: int) -> Tuple[int, str]:
        """读取帧头信息"""
        # 循环迭代四次获取完整帧体长
        # frame_body_length += (buffer[cursor] << (i * 8)) & 0xFFFFFFFF  # i = cursor = (0,1,2,3)
        frame_body_length = struct.unpack_from('<I', buffer, cursor)[0]
        return frame_body_length, "frame_body"

    @staticmethod
    def _read_frame_body(buffer: bytearray, cursor: int, length: int) -> bytes:
        """读取帧体数据"""
        frame_body = buffer[cursor:cursor + length]
        if frame_body[:2] != b'\xFF\xD8':
            raise StreamHandleError("无效的JPEG头")
        return frame_body


class MiniCap(ScreenCap):
    """MiniCap 截图类"""

    def __init__(
            self,
            serial: str,
            rate: Optional[int] = None,
            quality: int = 100,
            timeout: Optional[int] = None,
            host: str = DEFAULT_HOST,
            skip_frame: bool = True,
            use_stream: bool = True
    ):
        """
        初始化 MiniCap 截图对象
        
        Args:
            serial: 设备序列号
            rate: 截图帧率，None表示自动
            quality: 图像质量(1-100)
            timeout: 超时时间(ms)
            host: 连接地址（默认：127.0.0.1）
            skip_frame: 当处理帧的速度跟不上捕获速度时,是否跳过它们
            use_stream: 是否使用流模式
            
        Raises:
            MiniCapUnSupportError: 当设备不支持MiniCap时抛出
        """

        self.minicap = MiniCapManager(serial, rate, quality, timeout, host, skip_frame, use_stream)

    def screencap(self) -> np.ndarray:
        """
        捕获屏幕内容
        
        Returns:
            np.ndarray: RGB格式的图像数组
            
        Raises:
            RuntimeError: 当捕获或转换失败时抛出
        """
        try:
            # 获取图像数据
            data = (self.minicap.stream.capture_frame() if self.minicap.config['use_stream']
                    else self.minicap.capture_frame())

            # 转换为numpy数组
            image = Image.open(io.BytesIO(data))
            return np.array(image)[:, :, :3]  # default 3

        except Exception as e:
            raise RuntimeError(f"屏幕捕获失败: {e}")


if __name__ == "__main__":
    m = MiniCap("127.0.0.1:16384")
    m.save_screencap()
    m.minicap.stop_minicap_service()
    pass
