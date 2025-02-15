from threading import Lock
from typing import Optional, Union, Tuple

import numpy as np
from adbutils import adb

from autosnapmanager.actions.clicks.android.touch import Touch
from autosnapmanager.managers.manager import Manager
from autosnapmanager.managers.manager_config import System, ScreenCaps, Matches, Clicks
from autosnapmanager.matches.match import Match
from autosnapmanager.screencaps.screencap import ScreenCap
from autosnapmanager.utils.logger import logger


class AndroidManager(Manager):
    def __init__(self,
                 serial: str,
                 screencap: Optional[Union[str, ScreenCaps, ScreenCap]] = None,
                 match: Optional[Union[str, Matches, Match]] = None,
                 click: Optional[Union[str, Clicks, Touch]] = None
                 ):
        """
        初始化 AndroidManager 对象

        Args:
            serial: 设备名
            screencap: 截图方法
            match: 匹配方法
            click: 点击方法
        """
        logger.info(f"正在连接设备: {adb.connect(serial)}")

        super().__init__(System.Android, serial, screencap, match, click)

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

    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int) -> None:
        self.clicks.swipe(start_x, start_y, end_x, end_y)


if __name__ == '__main__':
    a = AndroidManager(serial="127.0.0.1:16384", screencap=ScreenCaps.Adb, click=Clicks.Adb)
    a.click((200, 100))
    # logger.info(f"正在连接设备: {adb.connect(serial)}")
