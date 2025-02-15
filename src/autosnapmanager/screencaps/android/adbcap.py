import numpy as np
from adbutils import adb
from autosnapmanager.screencaps.screencap import ScreenCap
from autosnapmanager.utils.logger import logger


class ADBCap(ScreenCap):
    """
    ADB截图类，用于通过ADB捕获Android设备屏幕内容
    
    继承自ScreenCap抽象基类，实现了ADB截图的具体逻辑
    """

    __slots__ = ('__adb',)

    def __init__(self, serial: str) -> None:
        """
        初始化ADB截图对象
        
        Args:
            serial (str): Android设备序列号或地址，如 "127.0.0.1:16384"
        """
        self._adb = adb.device(serial)

    def screencap(self) -> np.ndarray:
        """
        通过ADB捕获设备屏幕内容
        
        Returns:
            np.ndarray: 包含设备屏幕内容的numpy数组(RGB格式)
            
        Raises:
            RuntimeError: 当无法通过ADB捕获屏幕时抛出
        """
        try:
            img = self._adb.screenshot()
            img_array = np.array(img)

            # 处理4通道RGBA图像
            if img_array.ndim == 3 and img_array.shape[2] == 4:
                return img_array[:, :, :3]  # 移除alpha通道

            return img_array

        except Exception as e:
            logger.error(f"ADB截图失败: {str(e)}")
            raise RuntimeError(f"无法通过ADB捕获屏幕: {str(e)}")


if __name__ == "__main__":
    import time

    start_time = time.time()
    adb_cap = ADBCap("127.0.0.1:16384")
    adb_cap.save_screencap()
    logger.info(f"运行时间：{time.time() - start_time}")
