"""
PyAutoGui点击模块
使用pyautogui实现屏幕点击功能
"""

import pyautogui

from actions.clicks.click import Click
from utils.logger import logger
from utils.window_tools import get_window


class PyAutoGuiClick(Click):
    """使用PyAutoGui实现的点击类"""

    def __init__(self, window_name: str = None):
        self._window = get_window(window_name) if window_name else None

    def click(self, x: int, y: int) -> None:
        """
        在指定坐标执行点击
        
        Args:
            x: 点击位置的横坐标
            y: 点击位置的纵坐标
            
        Raises:
            RuntimeError: 点击操作失败时抛出
        """
        try:
            if self._window:
                window_left, window_top = self._window.left, self._window.top
                x += window_left
                y += window_top

            if not (0 <= x < pyautogui.size().width and 0 <= y < pyautogui.size().height):
                raise ValueError(f"坐标 ({x}, {y}) 超出屏幕范围。")

            pyautogui.click(x=x, y=y, button='left')
            logger.debug(f"点击执行完成: ({x}, {y})")

        except Exception as e:
            logger.error(f"点击执行失败: {e}")
            raise RuntimeError(f"PyAutoGui点击失败: {e}")

    @classmethod
    def click_image(cls, image_path: str) -> bool:
        """
        点击屏幕上匹配的图像位置
        
        Args:
            image_path: 目标图像的路径
            
        Returns:
            bool: 是否成功找到并点击了图像
            
        Raises:
            RuntimeError: 点击操作失败时抛出
        """
        try:
            location = pyautogui.locateCenterOnScreen(image_path, confidence=0.9)
            logger.debug(f"图像位置: {location}")
            if location:
                pyautogui.click(location)
                logger.debug(f"图像点击完成: {image_path}")
                return True

            logger.debug(f"未找到目标图像: {image_path}")
            return False

        except Exception as e:
            logger.error(f"图像点击失败: {e}")
            raise RuntimeError(f"PyAutoGui图像点击失败: {e}")


if __name__ == "__main__":
    # # 基本点击测试
    # clicker = PyAutoGuiClick()
    # clicker.clicks(100, 100)

    # # 图像点击测试
    # success = PyAutoGuiClick.click_image(
    #     r"/temp/tmp4D71.png")
    # print(f"图像点击{'成功' if success else '失败'}")
    pass
