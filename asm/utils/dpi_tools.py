import ctypes
from typing import Callable
from utils.logger import logger

# 定义DPI_AWARENESS_CONTEXT常量
DPI_AWARENESS_CONTEXT_UNAWARE = ctypes.c_void_p(-1)
DPI_AWARENESS_CONTEXT_SYSTEM_AWARE = ctypes.c_void_p(-2)
DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE = ctypes.c_void_p(-3)
DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 = ctypes.c_void_p(-4)

# 定义 DPI_AWARENESS 常量
DPI_AWARENESS_UNAWARE = 0
DPI_AWARENESS_SYSTEM_AWARE = 1
DPI_AWARENESS_PER_MONITOR_AWARE = 2


def is_dpi_awareness_set() -> bool:
    """
    检查DPI感知是否已经被设置。
    """
    return True if ctypes.windll.user32.IsProcessDPIAware() else False


def set_dpi_awareness() -> None:
    """
    设置进程的DPI感知级别

    尝试按以下顺序设置DPI感知:
    1. SetProcessDpiAwarenessContext (Windows 10 1607+)
    2. SetProcessDpiAwarenessContext (V1版本，兼容性)
    3. SetProcessDpiAwareness (Windows 8.1+)
    4. SetProcessDPIAware (早期Windows版本)

    Raises:
        OSError: 当所有DPI设置方法都失败时抛出
    """
    if is_dpi_awareness_set():
        logger.debug("DPI感知已设置")
        return

    def try_set_dpi(func: Callable, *args) -> bool:
        """尝试使用指定方法设置DPI感知"""
        try:
            result = func(*args)
            return result != 0 if func.__name__ == "SetProcessDpiAwarenessContext" else result == 0 or result is None
        except Exception:
            return False

    dpi_awareness_methods = [
        (ctypes.windll.user32.SetProcessDpiAwarenessContext, DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2),
        (ctypes.windll.user32.SetProcessDpiAwarenessContext, DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE),
        (ctypes.OleDLL('shcore').SetProcessDpiAwareness, DPI_AWARENESS_PER_MONITOR_AWARE),
        (ctypes.windll.user32.SetProcessDPIAware, None)  # 最后尝试SetProcessDPIAware，不需要参数
    ]

    for func, arg in dpi_awareness_methods:
        args = () if arg is None else (arg,)
        if try_set_dpi(func, *args):
            method_name = func.__name__
            if method_name == "SetProcessDpiAwarenessContext":
                if arg == DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2:
                    logger.debug("已使用DPI感知V2设置")
                else:
                    logger.debug("已使用DPI感知V1设置")
            elif method_name == "SetProcessDpiAwareness":
                logger.debug("已使用Shcore DPI感知设置")
            else:
                logger.debug("已使用基础DPI感知设置")
            return

    logger.error("DPI感知设置失败")
    raise OSError("无法设置DPI感知，当前Windows版本可能不支持")


if __name__ == '__main__':
    set_dpi_awareness()
