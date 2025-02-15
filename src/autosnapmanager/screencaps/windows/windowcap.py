from ctypes import windll
from win32gui import GetClientRect, GetWindowDC, ReleaseDC, DeleteObject
from win32ui import CreateDCFromHandle, CreateBitmap
import numpy as np
from autosnapmanager.screencaps.screencap import ScreenCap
from autosnapmanager.utils.logger import logger
from autosnapmanager.utils.window_tools import get_hwnd


class WindowCap(ScreenCap):
    """
    窗口截图类，用于捕获指定窗口的图像内容

    继承自ScreenCap抽象基类，实现了窗口截图的具体逻辑
    """

    def __init__(self, window_name: str):
        """
        初始化窗口截图对象
        
        Args:
            window_name (str): 要捕获的窗口名称
        """
        self.window_name: str = window_name
        self.hwnd: int = get_hwnd(window_name)

    def screencap(self) -> np.ndarray:
        """
        捕获指定窗口的屏幕内容
        
        Returns:
            np.ndarray: 包含窗口图像内容的numpy数组(RGB格式)
            
        Raises:
            RuntimeError: 当无法捕获窗口图像时抛出
        """
        # 获取窗口客户区域大小
        rect = GetClientRect(self.hwnd)
        width = rect[2] - rect[0]
        height = rect[3] - rect[1]

        # 创建设备上下文
        window_dc = None
        dc_obj = None
        compatible_dc = None
        bitmap = None

        try:
            window_dc = GetWindowDC(self.hwnd)
            dc_obj = CreateDCFromHandle(window_dc)
            compatible_dc = dc_obj.CreateCompatibleDC()

            # 创建位图对象
            bitmap = CreateBitmap()
            bitmap.CreateCompatibleBitmap(dc_obj, width, height)
            compatible_dc.SelectObject(bitmap)

            # 捕获窗口内容
            if not windll.user32.PrintWindow(self.hwnd, compatible_dc.GetSafeHdc(), 3):
                raise RuntimeError(f"无法捕获窗口: {self.window_name} 的图像！")

            # 转换为numpy数组
            bitmap_info = bitmap.GetInfo()
            bitmap_bits = bitmap.GetBitmapBits(True)

            # 处理图像数据
            img_array = np.frombuffer(bitmap_bits, dtype=np.uint8).reshape(
                (bitmap_info["bmHeight"], bitmap_info["bmWidth"], 4)
            )
            # BGR转RGB并移除alpha通道
            return img_array[:, :, [2, 1, 0]][:, :, :3]

        except Exception as e:
            logger.error(f"截图过程发生错误: {str(e)}")
            raise

        finally:
            # 清理资源
            if dc_obj:
                dc_obj.DeleteDC()
            if compatible_dc:
                compatible_dc.DeleteDC()
            if window_dc:
                ReleaseDC(self.hwnd, window_dc)
            if bitmap:
                DeleteObject(bitmap.GetHandle())


if __name__ == "__main__":
    import time
    from src.autosnapmanager.utils import set_dpi_awareness

    start_time = time.time()
    set_dpi_awareness()
    window_cap = WindowCap("智谱清言")
    image = window_cap.screencap()
    window_cap.save_screencap(image)
    end_time = time.time()
    logger.debug(f"运行时间：{end_time - start_time}")
