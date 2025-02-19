from typing import Optional, Union, Tuple, List

import numpy as np
from adbutils import adb

from autosnapmanager.actions.clicks.android.touch import Touch
from autosnapmanager.managers.manager import Manager
from autosnapmanager.managers.manager_config import System, ScreenCaps, Matches, Clicks, DefaultArgs
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

        for key in ['ScreenCap', 'Click']:
            DefaultArgs[System.Android][key]['serial'] = serial

        super().__init__(system=System.Android, params=DefaultArgs[System.Android], screencap=screencap, match=match,
                         click=click)

    def screenshot(self, save_path: str = None) -> None:
        """获取屏幕截图"""
        self.screenCaps.save_screencap(save_path)

    def match(self, template: str, threshold: float = None) -> bool:
        """匹配模板"""
        return self.matches.match(self.screenCaps.screencap(), template, threshold)

    def click(self, template: Union[str, tuple], threshold: float = None,
              repeat: bool = False, min_distance: Tuple[int, int] = (1, 1),
              duration: int = None
              ) -> None:
        """点击匹配位置, 接受图片路径与点击坐标元组"""
        if isinstance(template, str):
            x, y = self._locate_center(template, threshold) \
                if not repeat \
                else self._locate_center_repeated(template, min_distance, threshold)
        else:
            x, y = template

        with self.click_lock:
            self.clicks.click(x, y, duration=duration)

    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int) -> None:
        self.clicks.swipe(start_x, start_y, end_x, end_y)

    def _locate_center(self, template: Union[str, np.ndarray], threshold: float = None) -> Tuple[int, int]:
        """定位匹配区域最大相似度的中心坐标"""
        return self.matches.locate_center(self.screenCaps.screencap(), template, threshold)

    def _locate_center_repeated(self, template: Union[str, np.ndarray],
                                min_distance: Tuple[int, int] = (0, 0),
                                threshold: float = None
                                ) -> Tuple[List[int], List[int]]:
        """定位匹配区域中指定阈值内的所有中心坐标"""
        return self.matches.locate_center_repeated(self.screenCaps.screencap(), template, min_distance, threshold)


if __name__ == '__main__':
    a = AndroidManager(serial="127.0.0.1:16384", screencap=ScreenCaps.Adb, click=Clicks.Adb)
    a.click((200, 100))
    # logger.info(f"正在连接设备: {adb.connect(serial)}")
