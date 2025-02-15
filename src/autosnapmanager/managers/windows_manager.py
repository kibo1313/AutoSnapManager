from threading import Lock
from typing import Union, Tuple, Optional

import numpy as np

from autosnapmanager.actions.clicks.click import Click
from autosnapmanager.managers.manager import Manager
from autosnapmanager.managers.manager_config import System, ScreenCaps, Matches, Clicks
from autosnapmanager.matches.match import Match
from autosnapmanager.screencaps.screencap import ScreenCap
from autosnapmanager.utils.dpi_tools import set_dpi_awareness


class WindowsManager(Manager):
    def __init__(self,
                 window_name: Optional[str] = None,
                 screencap: Optional[Union[str, ScreenCaps, ScreenCap]] = None,
                 match: Optional[Union[str, Matches, Match]] = None,
                 click: Optional[Union[str, Clicks, Click]] = None
                 ):
        """
        初始化 WindowsManager 对象

        Args:
            window_name: 目标窗口名称
            screencap: 截图方法类
            match: 匹配方法类
            click: 点击方法类
        """
        set_dpi_awareness()  # 设置DPI感知

        super().__init__(System.Windows, window_name, screencap, match, click)

        self.click_lock = Lock()

    def screenshot(self, save_path: str = None) -> None:
        """获取屏幕截图"""
        self.screenCaps.save_screencap(save_path)

    def match(self, template: str, threshold: float = None) -> bool:
        """匹配模板"""
        return self.matches.match(self.screenCaps.screencap(), template, threshold)

    def _locate_center(self, template: Union[str, np.ndarray]) -> Tuple[int, int]:
        """定位匹配区域的中心坐标"""
        return self.matches.locate_center(self.screenCaps.screencap(), template)

    def click(self, template: Union[str, tuple]) -> None:
        """点击匹配位置"""
        if isinstance(template, str):
            x, y = self._locate_center(template)
        else:
            x, y = template[0], template[1]

        with self.click_lock:
            self.clicks.click(x, y)


if __name__ == "__main__":
    win = WindowsManager()
    win.screenshot()
