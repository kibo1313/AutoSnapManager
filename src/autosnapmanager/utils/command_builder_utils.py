"""
命令构建工具
用于构建 minitouch 的命令字符串，支持自定义触摸操作序列

使用示例:
    with safe_connection(_DEVICE_ID) as connection:
        builder = CommandBuilder()
        builder.down(0, 400, 400, 50)  # 手指按下
        builder.commit()
        builder.move(0, 500, 500, 50)  # 移动
        builder.commit()
        builder.up(0)  # 抬起
        builder.commit()
        builder.publish(connection)  # 执行
"""

import socket
import time
from dataclasses import dataclass, field
from typing import List

from autosnapmanager.actions.clicks.android.touch_config import DEFAULT_DELAY, DEFAULT_CHARSET


@dataclass
class CommandBuilder:
    """
    minitouch 命令构建器
    用于构建和执行触摸操作命令序列
    """
    _socket: socket.socket
    _commands: List[str] = field(default_factory=list)  # 命令列表
    _delay: int = field(default=0)  # 累计延迟时间(ms)

    def append(self, command: str) -> None:
        """添加命令到命令列表"""
        self._commands.append(command)

    def commit(self) -> None:
        """提交当前操作 'c\n' """
        self.append("c")

    def wait(self, ms: int) -> None:
        """添加等待命令 'w <ms>\n' """
        self.append(f"w {ms}")
        self._delay += ms

    def waitTo(self, ms: int) -> None:
        self.wait(ms)
        self.publish()

    def up(self, contact_id: int) -> None:
        """
        添加手指抬起命令 'u <contact_id>\n'
        
        Args:
            contact_id: 触点ID
        """
        self.append(f"u {contact_id}")

    def upTo(self, contact_id: int) -> None:
        self.up(contact_id)
        self.publish()

    def down(self, contact_id: int, x: int, y: int, pressure: int) -> None:
        """
        添加手指按下命令 'd <contact_id> <x> <y> <pressure>\n'
        
        Args:
            contact_id: 触点ID
            x: 横坐标
            y: 纵坐标
            pressure: 压力值(0-255)
        """
        self.append(f"d {contact_id} {x} {y} {pressure}")

    def downTo(self, contact_id: int, x: int, y: int, pressure: int) -> None:
        self.down(contact_id, x, y, pressure)
        self.publish()

    def move(self, contact_id: int, x: int, y: int, pressure: int) -> None:
        """
        添加手指移动命令 'm <contact_id> <x> <y> <pressure>\n'
        
        Args:
            contact_id: 触点ID
            x: 横坐标
            y: 纵坐标
            pressure: 压力值(0-255)
        """
        self.append(f"m {contact_id} {x} {y} {pressure}")

    def moveTo(self, contact_id: int, x: int, y: int, pressure: int) -> None:
        self.move(contact_id, x, y, pressure)
        self.publish()

    def publish(self) -> None:
        """执行当前命令序列"""
        try:
            self.commit()
            commands = "\n".join(self._commands) + "\n"
            # 发送命令到设备
            self.send(commands)
            time.sleep(self._delay / 1000 + DEFAULT_DELAY)
        finally:
            self.reset()

    def send(self, command: str) -> None:
        """传输命令至套接字"""
        self._socket.sendall(command.encode(DEFAULT_CHARSET))

    def reset(self) -> None:
        """重置命令构建器状态"""
        self._commands.clear()
        self._delay = 0
