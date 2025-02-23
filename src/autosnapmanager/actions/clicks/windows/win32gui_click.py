"""
Win32Gui点击模块
使用win32gui.SendMessage实现窗口点击功能
"""

from win32gui import SendMessage
from win32con import WM_LBUTTONDOWN, WM_LBUTTONUP, MK_LBUTTON

from autosnapmanager.actions.clicks.click import Click
from autosnapmanager.utils.logger import logger
from autosnapmanager.utils.window_tools import get_window_rect, get_hwnd


class Win32GuiClick(Click):
    """使用Win32Gui实现的点击类"""

    __slots__ = ('_hwnd', 'window_width', 'window_height')

    def __init__(self, window_name: str = None) -> None:
        """
        初始化Win32Gui点击对象
        
        Args:
            window_name: 目标窗口名
        """
        self._hwnd = get_hwnd(window_name)
        _, _, self.window_width, self.window_height = get_window_rect(window_name)

    def click(self, x: int, y: int) -> None:
        """
        在指定坐标执行点击
        
        Args:
            x: 点击位置的横坐标
            y: 点击位置的纵坐标
            
        Raises:
            RuntimeError: 发送消息失败时抛出
        """
        if x < 0 or x > self.window_width or y < 0 or y > self.window_height:
            raise ValueError(f"坐标 ({x}, {y}) 超出屏幕范围。")
        try:
            # 计算消息参数
            lparam = self._make_lparam(x, y)

            # 发送鼠标按下消息
            SendMessage(self._hwnd, WM_LBUTTONDOWN, MK_LBUTTON, lparam)
            # 发送鼠标抬起消息
            SendMessage(self._hwnd, WM_LBUTTONUP, 0, lparam)

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
        # numpy.int32，可能与 Python 原生int不兼容,必须强转
        return (int(y) << 16) | int(x)


if __name__ == "__main__":
    from autosnapmanager.utils.dpi_tools import set_dpi_awareness

    # 设置DPI感知
    set_dpi_awareness()

    # 测试点击
    clicker = Win32GuiClick("历史记录")
    clicker.click(787, 431)
