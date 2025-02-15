"""
图像处理工具模块
提供图像验证、转换等功能
"""

from typing import Optional, Tuple, Union
from pathlib import Path
import numpy as np
import cv2
from PIL import Image

from autosnapmanager.utils.logger import logger


def image2array(image: Union[str, Path, Image.Image, np.ndarray]) -> np.ndarray:
    """
    将不同类型的图像转换为numpy数组
    
    Args:
        image: 要转换的图像，支持:
            - 字符串或Path路径
            - PIL.Image对象
            - numpy数组
            
    Returns:
        np.ndarray: RGB格式的图像数组
        
    Raises:
        TypeError: 当输入类型不支持时抛出
        ValueError: 当图像无效时抛出
    """
    try:
        if isinstance(image, (str, Path)):
            # 从文件路径读取
            img_array = cv2.imread(str(image))
            if img_array is None:
                raise ValueError(f"无法读取图像文件: {image}")
            return cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)

        elif isinstance(image, Image.Image):
            # 从PIL.Image转换
            return np.array(image)

        elif isinstance(image, np.ndarray):
            # 已经是numpy数组
            return image

        else:
            raise TypeError(f"不支持的图像类型: {type(image)}")

    except Exception as e:
        logger.error(f"图像转换失败: {e}")
        raise RuntimeError(f"转换为numpy数组失败: {e}")


def check_image_array(
        image: np.ndarray,
        channels: Optional[int] = None,
        dtype: Optional[type] = None
) -> None:
    """
    验证图像数组的有效性
    
    Args:
        image: 要验证的图像数组
        channels: 期望的通道数，None表示不检查
        dtype: 期望的数据类型，None表示不检查
        
    Raises:
        TypeError: 当输入类型不是numpy数组时抛出
        ValueError: 当图像格式不符合要求时抛出
    """
    if not isinstance(image, np.ndarray):
        raise TypeError(f"输入必须是numpy数组，而不是 {type(image)}")

    if channels is not None and image.ndim != 3:
        raise ValueError(f"图像必须是3维数组，当前维度: {image.ndim}")

    if channels is not None and image.shape[2] != channels:
        raise ValueError(f"图像必须是{channels}通道，当前通道数: {image.shape[2]}")

    if dtype is not None and image.dtype != dtype:
        raise ValueError(f"图像数据类型必须是{dtype}，当前类型: {image.dtype}")


def convert_color(
        image: np.ndarray,
        src_color: str,
        dst_color: str
) -> np.ndarray:
    """
    转换图像颜色空间
    
    Args:
        image: 要转换的图像数组
        src_color: 源颜色空间 ('RGB', 'BGR', 'GRAY')
        dst_color: 目标颜色空间 ('RGB', 'BGR', 'GRAY')
        
    Returns:
        np.ndarray: 转换后的图像数组
        
    Raises:
        ValueError: 当颜色空间参数无效时抛出
    """
    color_codes = {
        'BGR2RGB': cv2.COLOR_BGR2RGB,
        'RGB2BGR': cv2.COLOR_RGB2BGR,
        'BGR2GRAY': cv2.COLOR_BGR2GRAY,
        'RGB2GRAY': cv2.COLOR_RGB2GRAY,
        'GRAY2BGR': cv2.COLOR_GRAY2BGR,
        'GRAY2RGB': cv2.COLOR_GRAY2RGB
    }

    conversion = f"{src_color}2{dst_color}"
    if conversion not in color_codes:
        raise ValueError(f"不支持的颜色空间转换: {conversion}")

    try:
        return cv2.cvtColor(image, color_codes[conversion])
    except Exception as e:
        logger.error(f"颜色空间转换失败: {e}")
        raise RuntimeError(f"图像转换失败: {e}")


def resize_image(
        image: np.ndarray,
        size: Union[float, Tuple[int, int]],
        interpolation: int = cv2.INTER_LINEAR,
        keep_ratio: bool = True
) -> np.ndarray:
    """
    调整图像大小
    
    Args:
        image: 要调整的图像数组
        size: 目标大小（缩放比例或(宽度,高度)元组）
        interpolation: OpenCV 插值方法
        keep_ratio: 是否保持宽高比
        
    Returns:
        np.ndarray: 调整后的图像数组
        
    Raises:
        ValueError: 当参数无效时抛出
    """
    try:
        if isinstance(size, (int, float)):
            if not 0 < size <= 10:
                raise ValueError("缩放比例必须在0-10之间")
            height, width = image.shape[:2]
            new_width = int(width * size)
            new_height = int(height * size)
        else:
            if not all(x > 0 for x in size):
                raise ValueError("尺寸必须为正数")
            new_width, new_height = size

        if keep_ratio:
            current_ratio = image.shape[1] / image.shape[0]
            target_ratio = new_width / new_height

            if current_ratio > target_ratio:
                new_height = int(new_width / current_ratio)
            else:
                new_width = int(new_height * current_ratio)

        return cv2.resize(image, (new_width, new_height), interpolation=interpolation)

    except Exception as e:
        logger.error(f"图像缩放失败: {e}")
        raise RuntimeError(f"调整图像大小失败: {e}")


if __name__ == "__main__":
    pass
