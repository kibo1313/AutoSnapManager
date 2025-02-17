import ctypes
from time import sleep
from typing import Tuple

import pygetwindow as gw
import win32gui

from autosnapmanager.utils.logger import logger


def get_window(window_name: str) -> gw.Window:
    """
    获取窗口对象


    Args:
        window_name (str): 要获取的窗口名称

    Returns:
        gw.Window: pygetwindow窗口对象

    Raises:
        ValueError: 找不到指定窗口时抛出
    """

    try:
        if window_name is None:
            raise ValueError("窗口名不能为None！")

        windows = gw.getWindowsWithTitle(window_name)
        if not windows:
            raise ValueError(f"未找到窗口: {window_name}")
        return windows[0]
    except Exception as e:
        logger.error(f"获取窗口失败: {e}")
        raise


def get_hwnd(window_name: str) -> int:
    """
    通过窗口标题获取窗口句柄（支持模糊匹配）

    Args:
        window_name (str): 窗口标题（支持部分匹配）

    Returns:
        int: 窗口句柄

    Raises:
        ValueError: 找不到窗口时抛出
    """

    def enum_handler(hwnd, ctx):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if window_name.lower() in title.lower():
                ctx.append(hwnd)
        return True

    if not window_name:
        raise ValueError("窗口名不能为空")

    handles = []
    win32gui.EnumWindows(enum_handler, handles)

    if not handles:
        raise ValueError(f"未找到窗口: {window_name}")

    # 返回最顶层匹配窗口
    return handles[0]


def get_client_origin(hwnd: int) -> Tuple[int, int]:
    """获取窗口客户区在屏幕的位置"""
    return win32gui.ClientToScreen(hwnd, (0, 0))


def window_to_top(window_name: str, width: int, height: int, x: int = 0, y: int = 0) -> None:
    """
    将应用窗口置顶并调整大小位置
    
    Args:
        window_name (str): 要操作的窗口名称
        width (int): 窗口指定的宽
        height (int): 窗口指定的高
        x (int, optional): 窗口左上角X轴坐标. 默认为0
        y (int, optional): 窗口左上角Y轴坐标. 默认为0
    """
    try:
        window = get_window(window_name)
        logger.info(f"窗口原始状态：{window}")

        window.restore()  # 恢复窗口
        window.resizeTo(width, height)  # 调整大小
        window.moveTo(x, y)  # 移动位置
        window.activate()  # 激活窗口

        sleep(1)  # 等待窗口状态更新
        logger.info(f"窗口当前状态：{window}")

    except Exception as e:
        logger.error(f"窗口置顶操作失败: {e}")
        raise


def get_screen_scale_factors() -> Tuple[float, float]:
    """
    获取电脑屏幕缩放率
    
    Returns:
        Tuple[float, float]: (水平缩放率, 垂直缩放率)
        缩放率相对于96 DPI的比例，如1.25表示125%缩放
        
    Raises:
        RuntimeError: 获取缩放率失败时抛出
    """
    try:
        # 设置进程DPI感知
        ctypes.windll.shcore.SetProcessDpiAwareness(1)

        # 获取DC句柄
        hdc = ctypes.windll.user32.GetDC(0)
        if not hdc:
            raise RuntimeError("无法获取显示设备上下文")

        try:
            # 获取DPI值
            dpi_x = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)  # LOGPIXELSX
            dpi_y = ctypes.windll.gdi32.GetDeviceCaps(hdc, 90)  # LOGPIXELSY

            # 计算缩放比例
            return dpi_x / 96.0, dpi_y / 96.0

        finally:
            # 释放DC句柄
            ctypes.windll.user32.ReleaseDC(0, hdc)

    except Exception as e:
        logger.error(f"获取屏幕缩放率失败: {e}")
        raise RuntimeError(f"无法获取屏幕缩放率: {e}")
