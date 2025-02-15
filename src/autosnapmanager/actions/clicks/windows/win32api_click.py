"""
Win32Api点击模块
使用win32api.PostMessage实现窗口点击功能
"""

from win32api import PostMessage
from win32con import WM_LBUTTONDOWN, WM_LBUTTONUP, MK_LBUTTON

from autosnapmanager.actions.clicks.click import Click
from autosnapmanager.utils.logger import logger
from autosnapmanager.utils.window_tools import get_hwnd


class Win32ApiClick(Click):
    """使用Win32Api实现的点击类"""

    __slots__ = ('_hwnd',)

    def __init__(self, window_name: str = None) -> None:
        """
        初始化Win32Api点击对象
        
        Args:
            window_name: 目标窗口名
        """
        self._hwnd = get_hwnd(window_name)

    def click(self, x: int, y: int) -> None:
        """
        在指定坐标执行点击
        
        Args:
            x: 点击位置的横坐标
            y: 点击位置的纵坐标
            
        Raises:
            RuntimeError: 发送消息失败时抛出
        """
        try:
            # 计算消息参数
            lparam = self._make_lparam(x, y)

            # 发送鼠标按下消息
            PostMessage(self._hwnd, WM_LBUTTONDOWN, MK_LBUTTON, lparam)
            # 发送鼠标抬起消息
            PostMessage(self._hwnd, WM_LBUTTONUP, MK_LBUTTON, lparam)

            logger.debug(f"点击执行完成: ({x}, {y})")

        except Exception as e:
            logger.error(f"点击执行失败: {e}")
            raise RuntimeError(f"发送点击消息失败: {e}")

    @staticmethod
    def _make_lparam(x: int, y: int) -> int:
        """
        生成消息参数

        Args:
            x: 横坐标
            y: 纵坐标

        Returns:
            int: 组合后的坐标参数
        """
        return (int(y) << 16) | int(x)


if __name__ == "__main__":
    from utils.dpi_tools import set_dpi_awareness

    # 设置DPI感知
    set_dpi_awareness()

    # 测试点击
    clicker = Win32ApiClick("智谱清言")
    clicker.click(166, 45)
