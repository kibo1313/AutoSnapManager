from ctypes import windll
from win32gui import GetWindowDC, ReleaseDC, DeleteObject
from win32ui import CreateDCFromHandle, CreateBitmap
from win32con import SRCCOPY
import numpy as np
from autosnapmanager.utils.logger import logger
from autosnapmanager.screencaps.screencap import ScreenCap


class FullScreenCap(ScreenCap):
    """
    全屏截图类，用于捕获Windows系统的整个屏幕内容(主屏幕)
    
    继承自ScreenCap抽象基类，实现了全屏截图的具体逻辑
    """

    def __init__(self):
        """初始化全屏截图对象"""
        # 获取屏幕尺寸
        self.width = windll.user32.GetSystemMetrics(0)  # SM_CXSCREEN
        self.height = windll.user32.GetSystemMetrics(1)  # SM_CYSCREEN

    def screencap(self) -> np.ndarray:
        """
        捕获整个屏幕内容
        
        Returns:
            np.ndarray: 包含屏幕内容的numpy数组(RGB格式)
            
        Raises:
            RuntimeError: 当无法捕获屏幕时抛出
        """
        # 创建设备上下文
        hwnd_dc = None
        mfc_dc = None
        save_dc = None
        bitmap = None

        try:
            # 获取屏幕DC
            hwnd_dc = GetWindowDC(0)
            mfc_dc = CreateDCFromHandle(hwnd_dc)
            save_dc = mfc_dc.CreateCompatibleDC()

            # 创建位图对象
            bitmap = CreateBitmap()
            bitmap.CreateCompatibleBitmap(mfc_dc, self.width, self.height)
            save_dc.SelectObject(bitmap)

            # 复制屏幕内容到位图
            save_dc.BitBlt(
                (0, 0), (self.width, self.height),
                mfc_dc, (0, 0),
                SRCCOPY
            )

            # 获取位图信息
            bmp_info = bitmap.GetInfo()
            bmp_bits = bitmap.GetBitmapBits(True)

            # 转换为numpy数组
            img_array = np.frombuffer(bmp_bits, dtype=np.uint8).reshape(
                (bmp_info["bmHeight"], bmp_info["bmWidth"], 4)
            )
            # BGR转RGB并移除alpha通道
            return img_array[:, :, [2, 1, 0]][:, :, :3]

        except Exception as e:
            logger.error(f"全屏截图失败: {str(e)}")
            raise RuntimeError(f"无法捕获屏幕: {str(e)}")

        finally:
            # 清理资源
            if bitmap:
                DeleteObject(bitmap.GetHandle())
            if save_dc:
                save_dc.DeleteDC()
            if mfc_dc:
                mfc_dc.DeleteDC()
            if hwnd_dc:
                ReleaseDC(0, hwnd_dc)


if __name__ == "__main__":
    import time
    from autosnapmanager.utils.dpi_tools import set_dpi_awareness

    start_time = time.time()

    set_dpi_awareness()
    screen_cap = FullScreenCap()
    screen_cap.save_screencap()

    end_time = time.time()
    logger.info(f"运行时间：{end_time - start_time}")
