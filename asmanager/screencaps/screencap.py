from abc import ABC, abstractmethod
import cv2
import numpy as np
from utils.process_file_tools import check_path
from utils.process_image_tools import check_image_array
from utils.logger import logger
from screencaps.screencap_config import IMG_SAVE_PATH, NOW_TIME


class ScreenCap(ABC):
    """屏幕截图抽象基类"""

    @abstractmethod
    def screencap(self) -> np.ndarray:
        """
        捕获屏幕内容
        
        Returns:
            np.ndarray: RGB格式的图像数组
        """

    def save_screencap(self, img: np.ndarray = None, save_path: str = None) -> None:
        """
        保存屏幕截图

        Args:
            img (np.ndarray): 要保存的图像数组(RGB格式，3通道)
            save_path (str): 保存路径

        Raises:
            RuntimeError: 当保存截图失败时抛出
        """
        try:
            img = self.screencap() if img is None else img

            check_image_array(img, channels=3, dtype=np.uint8)

            if save_path is None:
                save_path = IMG_SAVE_PATH
            check_path(save_path)

            img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            save_filename = f"{save_path}/{self.class_name}_{NOW_TIME}.png"

            logger.info(f"图片已保存至：{save_filename}") \
                if cv2.imwrite(save_filename, img_bgr) \
                else logger.info(f"路径识别错误：{save_filename}")

        except Exception as e:
            logger.error(f"保存截图失败: {str(e)}")
            raise RuntimeError(f"无法保存截图: {str(e)}")

    @property
    def class_name(self):
        """返回子类的类名，用于构造保存的文件名。"""
        return self.__class__.__name__
