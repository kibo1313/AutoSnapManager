from asyncio import Lock
from typing import Optional, Union, Any, Tuple

import numpy as np
from adbutils import adb

from actions.clicks.android.touch import Touch
from managers.manager import Manager
from managers.manager_config import CLASSMAP, DefaultMethods, System, ScreenCaps, Matches, Clicks
from matches.match import Match
from screencaps.screencap import ScreenCap
from utils.logger import logger
from utils.module_class import get_class_name, check_class_name, get_module_class as module


class AndroidManager(Manager):
    def __init__(self,
                 serial: Optional[str] = None,
                 screencap: Optional[Union[str, ScreenCaps, ScreenCap]] = None,
                 match: Optional[Union[str, Matches, Match]] = None,
                 click: Optional[Union[str, Clicks, Touch]] = None
                 ):
        logger.info(f"正在连接设备: {adb.connect(serial)}")

        self.serial = serial

        self.screenCaps = self._init_method(screencap, ScreenCap)
        self.matches = self._init_method(match, Match)
        self.clicks = self._init_method(click, Touch)

        self.click_lock = Lock()

    def screenshot(self, save_path: str = None) -> None:
        """获取屏幕截图"""
        self.screenCaps.save_screencap(save_path)

    def match(self, template: str) -> bool:
        """匹配模板"""
        return self.matches.match(self.screenCaps.screencap(), template)

    def _locate_center(self, template: Union[str, np.ndarray]) -> Tuple[int, int]:
        """定位匹配区域的中心坐标"""
        return self.matches.locate_center(self.screenCaps.screencap(), template)

    def click(self, template: str) -> None:
        """点击匹配位置"""
        x, y = self._locate_center(template)

        with self.click_lock:
            self.clicks.click(x, y)

    def clickTo(self, x: int, y: int) -> None:
        """点击指定位置"""
        with self.click_lock:
            self.clicks.click(x, y)

    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int) -> None:
        self.clicks.swipe(start_x, start_y, end_x, end_y)

    def _init_method(self, method: Any, super_class) -> Union[ScreenCap, Match, Touch]:
        """初始化方法类"""
        if method is None:
            return self._set_default_method(super_class)

        if isinstance(method, super_class):
            return method

        if isinstance(method, str):
            method = module(CLASSMAP[super_class.__name__], method, System.Android)
            return method(serial=self.serial)

        if isinstance(method, type) and issubclass(method, super_class):
            class_name = get_class_name(method)
            super_name = get_class_name(super_class)
            check_class_name(CLASSMAP[super_name], System.Android, class_name)
            return method(serial=self.serial)

        raise TypeError(f"传入的 '{method}' 参数未解析")

    def _set_default_method(self, super_class) -> Union[ScreenCap, Match, Touch]:
        """设置方法默认值"""
        default_methods = DefaultMethods.get(super_class.__name__).get(System.Android)
        map_table = CLASSMAP[super_class.__name__]

        return module(map_table, default_methods[0], System.Android)(serial=self.serial)


if __name__ == '__main__':
    a = AndroidManager(serial="127.0.0.1:16384", screencap=ScreenCaps.Adb)
    # logger.info(f"正在连接设备: {adb.connect(serial)}")
