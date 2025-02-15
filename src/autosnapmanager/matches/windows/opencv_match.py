"""
OpenCV 匹配模块
使用 OpenCV 实现图像匹配功能
"""
from typing import Union, Tuple, Generator

import cv2
import numpy as np

from autosnapmanager.matches.match import Match
from autosnapmanager.utils.logger import logger
from autosnapmanager.utils.process_image_tools import image2array, convert_color, resize_image
from autosnapmanager.utils.window_tools import get_screen_scale_factors


class OpenCVMatch(Match):
    def __init__(self,
                 param: str = None,
                 threshold: float = 0.9,
                 method: int = cv2.TM_CCOEFF_NORMED,
                 colors=False,
                 scale=False
                 ):
        """
        初始化 OpenCVMatch 对象

        Args:
            param: 占位
            threshold: 指定匹配阈值
            method: 指定匹配方法
            colors: 是否使用颜色匹配
            scale: 是否使用缩放（应对一个缩放率模板匹配多个缩放率图像的场景，模板缩放率默认100%）
        """
        self.threshold = threshold
        self.method = method
        self.colors = colors
        self.scale = scale
        self.template_scale_ratio: float = 1.0
        self.relative_scale_ratio: float = 0.0

    @property
    def template_scale_ratio(self) -> float:
        """获取模板缩放率"""
        return self._template_scale_ratio

    @template_scale_ratio.setter
    def template_scale_ratio(self, value: float):
        """设置模板缩放率"""
        if value <= 0:
            raise ValueError("缩放率必须大于0")
        self._template_scale_ratio = value

    def _get_threshold(self, threshold: float):
        """设置匹配阈值"""
        if threshold is not None:
            if not (0 <= threshold <= 1):
                raise ValueError("阈值必须在 [0, 1] 范围内")
            return threshold
        else:
            return self.threshold

    def match(self, image: Union[str, np.ndarray], template: Union[str, np.ndarray], threshold: float = None) -> bool:
        """
        匹配图像与模板

        Args:
            image: 输入图像，可以是路径或numpy数组
            template: 模板图像，可以是路径或numpy数组
            threshold: 指定匹配阈值

        Returns:
            bool: 匹配是否成功
        """
        threshold = self._get_threshold(threshold)
        try:
            self._get_matches(image, template, threshold)
            return True

        except ValueError:
            return False

    def _get_matches(self, image: Union[str, np.ndarray],
                     template: Union[str, np.ndarray],
                     threshold: float = None) -> np.ndarray:
        """获取匹配结果"""
        image = self._resize_img(image) if self.scale else image2array(image)
        template = image2array(template)

        image = convert_color(image, 'RGB', 'BGR' if self.colors else 'GRAY')
        template = convert_color(template, 'RGB', 'BGR' if self.colors else 'GRAY')

        result = cv2.matchTemplate(image, template, self.method)
        min_var, max_var, min_loc, max_loc = cv2.minMaxLoc(result)

        threshold = self._get_threshold(threshold)
        if max_var < threshold:
            raise ValueError(f"匹配失败 | 相似度: {max_var} | 阈值: {threshold}")

        logger.info(f"匹配成功 | 相似度: {max_var} | 阈值: {threshold}")
        return result

    def _locate_matches(self, image: Union[str, np.ndarray], template: Union[str, np.ndarray]):
        """
        定位匹配的最大左上角坐标

        Returns:
           Tuple[int, int]: 最大左上角坐标值（x, y）
        """
        matched_result = self._get_matches(image, template)
        _, _, _, max_loc = cv2.minMaxLoc(matched_result)

        if self.scale:
            # 将缩放后的坐标映射回原始坐标系统
            return tuple(int(coord / self.relative_scale_ratio) for coord in max_loc)

        return max_loc

    def locate_center(self, image: Union[str, np.ndarray], template: Union[str, np.ndarray]) -> Tuple[int, int]:
        """定位匹配区域中心点坐标"""
        template = image2array(template)
        height, width = template.shape[:2]
        max_loc = self._locate_matches(image, template)

        # 计算模板对应原图像缩放率的宽高
        scale_factor = self.relative_scale_ratio if self.scale else 1
        scale_width = int(width / scale_factor)
        scale_height = int(height / scale_factor)

        center = (int(max_loc[0] + scale_width / 2), int(max_loc[1] + scale_height / 2))
        logger.info(f"匹配中心点：{center}")

        return center

    def _resize_img(self, img: Union[str, np.ndarray],
                    keep_ratio: bool = True, interpolation: int = cv2.INTER_AREA) -> np.ndarray:
        """
        调整图片大小至指定缩放率

        Args:
            img: 要调整的图像，可以是路径或numpy数组
            keep_ratio: 是否保持宽高比
            interpolation: 插值方法

        Returns:
            np.ndarray: 调整后的图像数组

        Raises:
            ValueError: 当缩放率无效时抛出
        """
        # 获取缩放率
        scale = get_screen_scale_factors()

        if scale[0] != scale[1]:
            raise ValueError("屏幕宽高缩放率不一致！")
        if scale[0] < self.template_scale_ratio or scale[1] < self.template_scale_ratio:
            raise ValueError(f"屏幕缩放率需 ≥ {self.template_scale_ratio * 100}%")

        self.relative_scale_ratio = self.template_scale_ratio / scale[0]

        img = image2array(img)
        img = resize_image(img, self.relative_scale_ratio, keep_ratio=keep_ratio, interpolation=interpolation)

        return img

    def _locate_matches_repeated(
            self,
            image: Union[str, np.ndarray],
            template: Union[str, np.ndarray],
            min_distance: Tuple[int, int] = (0, 0)
    ) -> Generator[Tuple[int, int], None, None]:
        """
        定位模板在图像中所有匹配成功的左上角位置，并确保匹配区域之间不重合

        Args:
            min_distance: 匹配模板之间能容忍的最小间距
        yield:
            Tuple[int, int, float]: 左上角坐标值（x, y）和匹配值
        """
        result = self._get_matches(image, template)

        # 解析匹配位置坐标
        y_coords, x_coords = np.where(result >= self.threshold)
        matching_values = result[y_coords, x_coords]

        scale_factor = self.relative_scale_ratio if getattr(self, 'scale', False) else 1
        x_coords = np.round(x_coords / scale_factor).astype(int)
        y_coords = np.round(y_coords / scale_factor).astype(int)

        if min_distance[0] <= 0 and min_distance[1] <= 0:
            for x, y, value in zip(x_coords, y_coords, matching_values):
                yield x, y, value
        else:
            accepted_positions = set()  # 时间复杂度 O(1)
            min_distance_x, min_distance_y = min_distance
            for x, y, value in zip(x_coords, y_coords, matching_values):
                # 检查新位置是否与已接受的位置有重叠
                overlap = any(
                    abs(x - ax) <= min_distance_x and abs(y - ay) <= min_distance_y
                    for ax, ay in accepted_positions
                )
                if not overlap:
                    accepted_positions.add((x, y))
                    yield x, y, value

    def locate_center_repeated(self,
                               image: Union[str, np.ndarray],
                               template: Union[str, np.ndarray],
                               min_distance: Tuple[int, int] = (0, 0)
                               ) -> Generator[Tuple[int, int], None, None]:
        """
        定位模板在图像中所有匹配成功的中心坐标
        Args:
            image: 输入图像，可以是路径或numpy数组
            template: 模板图像，可以是路径或numpy数组
            min_distance: 匹配模板之间能容忍的最小间距
        yield:
            Tuple[int, int, float]: 左上角坐标值（x, y）和匹配值
        """
        template = image2array(template)
        height, width = template.shape[:2]

        scale_factor = self.relative_scale_ratio if self.scale else 1
        scaled_width = round(width / scale_factor)
        scaled_height = round(height / scale_factor)

        for num, (x, y, value) in enumerate(self._locate_matches_repeated(image, template, min_distance), start=1):
            # 计算中心坐标
            center_x = x + scaled_width // 2
            center_y = y + scaled_height // 2
            logger.debug(
                f"发现匹配点{num:<4} | "
                f"坐标: {str((x, y)):<14} | "
                f"中心: {str((center_x, center_y)):<14} | "
                f"匹配度: {value:.15f}")

            yield center_x, center_y
