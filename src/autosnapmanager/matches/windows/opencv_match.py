"""
OpenCV 匹配模块
使用 OpenCV 实现图像匹配功能
"""
from collections import defaultdict
from typing import Union, Tuple, Generator, List

import cv2
import numpy as np

from autosnapmanager.matches.match import Match
from autosnapmanager.utils.logger import logger
from autosnapmanager.utils.process_image_tools import image2array, convert_color, resize_image
from autosnapmanager.utils.window_tools import get_screen_scale_factors


class OpenCVMatchError(Exception):
    pass


class OpenCVMatch(Match):
    def __init__(self,
                 threshold: float = 0.9,
                 method: int = cv2.TM_CCOEFF_NORMED,
                 colors=False,
                 scale=False
                 ):
        """
        初始化 OpenCVMatch 对象

        Args:
            threshold: 指定匹配阈值
            method: 指定匹配方法
            colors: 是否使用颜色匹配
            scale: 是否使用缩放，适用于同一模板匹配多分辨率图像的场景，模板的默认缩放率为100%，仅支持windows端
        """
        self.threshold = threshold
        self.method = method
        self.colors = colors
        self.scale = scale

        if scale:
            self.screen_ratio = get_screen_scale_factors()
            self.template_scale_ratio: float = 1.0
            self._check_screen_ratio()
            self.relative_scale_ratio = self.template_scale_ratio / self.screen_ratio[0]

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

        except OpenCVMatchError:
            return False

    def _get_matches(self, image: Union[str, np.ndarray],
                     template: Union[str, np.ndarray],
                     threshold: float = None
                     ) -> np.ndarray:
        """获取匹配结果"""

        image = self._preprocess_image(image)
        template = self._preprocess_image(template, is_template=True)
        threshold = self._get_threshold(threshold)

        if template.shape[0] > image.shape[0] or template.shape[1] > image.shape[1]:
            raise ValueError("输入模板尺寸大于图像尺寸，请检查图像或模板是否合规")

        result = cv2.matchTemplate(image, template, self.method)
        min_var, max_var, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_var < threshold:
            logger.info(f"匹配失败 | 相似度: {max_var} | 阈值: {threshold}")
            raise OpenCVMatchError("未能在图像中找到模板")

        logger.info(f"匹配成功 | 相似度: {max_var} | 阈值: {threshold}")
        return result

    def _locate_matches(self, image: Union[str, np.ndarray], template: Union[str, np.ndarray], threshold: float = None):
        """
        定位匹配的最大左上角坐标

        Returns:
           Tuple[int, int]: 最大左上角坐标值（x, y）
        """
        threshold = self._get_threshold(threshold)
        matched_result = self._get_matches(image, template, threshold)
        _, _, _, max_loc = cv2.minMaxLoc(matched_result)

        if self.scale:
            # 将缩放后的坐标映射回原始坐标系统
            return tuple(int(coord / self.relative_scale_ratio) for coord in max_loc)

        return max_loc

    def locate_center(self, image: Union[str, np.ndarray], template: Union[str, np.ndarray],
                      threshold: float = None) -> Tuple[int, int]:
        """定位匹配区域中心点坐标"""
        template = image2array(template)
        height, width = template.shape[:2]
        threshold = self._get_threshold(threshold)

        max_loc = self._locate_matches(image, template, threshold)

        # 计算模板对应原图像缩放率的宽高
        scale_factor = self.relative_scale_ratio if self.scale else 1
        scale_width = int(width / scale_factor)
        scale_height = int(height / scale_factor)

        center = (int(max_loc[0] + scale_width / 2), int(max_loc[1] + scale_height / 2))
        logger.info(f"匹配中心点：{center}")

        return center

    def _locate_matches_repeated(
            self,
            image: Union[str, np.ndarray],
            template: Union[str, np.ndarray],
            min_distance: Tuple[int, int] = (0, 0),
            threshold: float = None
    ) -> Generator[Tuple[int, int, float], None, None]:
        """
        定位模板在图像中所有匹配成功的左上角位置，并确保匹配区域之间不重合

        Args:
            min_distance: 匹配模板之间能容忍的最小间距
        yield:
            Tuple[int, int, float]: 左上角坐标值（x, y）和匹配相似度
        """
        threshold = self._get_threshold(threshold)
        result = self._get_matches(image, template, threshold)

        # 解析匹配位置坐标
        y_coords, x_coords = np.where(result >= threshold)
        matching_values = result[y_coords, x_coords]
        # 匹配率降值索引值数组（优先处理高置信度点）
        sorted_indices = np.argsort(-matching_values)

        scale_factor = self.relative_scale_ratio if getattr(self, 'scale', False) else 1
        x_coords = np.round(x_coords / scale_factor).astype(int)
        y_coords = np.round(y_coords / scale_factor).astype(int)

        min_distance_x, min_distance_y = min_distance
        if min_distance_x <= 0 or min_distance_y <= 0:
            for idx in sorted_indices:
                yield x_coords[idx], y_coords[idx], matching_values[idx]

        else:
            # 基于网格空间划分的NMS算法，复杂度O(n)
            cell_size_x = min_distance_x
            cell_size_y = min_distance_y
            grid = defaultdict(list)

            def get_cell_key(cx, cy):
                return cx // cell_size_x, cy // cell_size_y

            def is_overlap(ix, iy):
                cell_key = get_cell_key(ix, iy)
                # 检查相邻9个单元格
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        check_key = (cell_key[0] + dx, cell_key[1] + dy)
                        if check_key in grid:
                            for (ax, ay) in grid[check_key]:
                                if abs(x - ax) <= min_distance_x and abs(y - ay) <= min_distance_y:
                                    return True
                return False

            for idx in sorted_indices:
                x = x_coords[idx]
                y = y_coords[idx]
                value = matching_values[idx]
                if not is_overlap(x, y):
                    grid[get_cell_key(x, y)].append((x, y))
                    yield x, y, value

    def locate_center_repeated(self,
                               image: Union[str, np.ndarray],
                               template: Union[str, np.ndarray],
                               min_distance: Tuple[int, int] = (0, 0),
                               threshold: float = None
                               ) -> Tuple[List[int], List[int]]:
        """
        定位模板在图像中所有匹配成功的中心坐标
        Args:
            image: 输入图像，可以是路径或numpy数组
            template: 模板图像，可以是路径或numpy数组
            min_distance: 匹配模板之间能容忍的最小间距
            threshold: 匹配阈值
        Returns:
            Tuple[List[int], List[int]: 中心坐标值列表（x, y）
        """
        threshold = self._get_threshold(threshold)
        template = image2array(template)
        height, width = template.shape[:2]

        scale_factor = self.relative_scale_ratio if self.scale else 1
        scaled_width = round(width / scale_factor)
        scaled_height = round(height / scale_factor)

        x_arr = []
        y_arr = []
        for num, (x, y, value) in enumerate(self._locate_matches_repeated(image, template, min_distance, threshold),
                                            start=1):
            # 计算中心坐标
            center_x = x + scaled_width // 2
            center_y = y + scaled_height // 2
            logger.debug(
                f"发现匹配点{num:<4} | "
                f"坐标: {str((x, y)):<14} | "
                f"中心: {str((center_x, center_y)):<14} | "
                f"匹配度: {value:.15f}")
            x_arr.append(center_x)
            y_arr.append(center_y)

        return x_arr, y_arr

    def _check_screen_ratio(self) -> None:
        """检查当前屏幕比例"""
        if self.screen_ratio[0] != self.screen_ratio[1]:
            raise ValueError("屏幕宽高缩放率不一致！")
        if self.screen_ratio[0] < self.template_scale_ratio or self.screen_ratio[1] < self.template_scale_ratio:
            raise ValueError(f"屏幕缩放率需 ≥ {self.template_scale_ratio * 100}%")

    def _preprocess_image(self, img: Union[str, np.ndarray], is_template: bool = False) -> np.ndarray:
        """预处理图像"""
        img = image2array(img)
        color_mode = 'BGR' if self.colors else 'GRAY'
        img = convert_color(img, 'RGB', color_mode)
        if self.scale and not is_template:
            img = self._resize_img(img)
        return img

    def _resize_img(self, img: Union[str, np.ndarray],
                    keep_ratio: bool = True, interpolation: int = cv2.INTER_AREA) -> np.ndarray:
        """
        调整图片大小至指定缩放率

        Args:
            img: 要调整的图像，可以是路径或numpy数组
            keep_ratio: 是否保持宽高比
            interpolation: 插值方法
        """
        img = resize_image(img, self.relative_scale_ratio, keep_ratio=keep_ratio, interpolation=interpolation)
        return img


if __name__ == '__main__':
    m = OpenCVMatch()
    tx, ty = m.locate_center_repeated(r"C:\Users\YXS\Downloads\t1.png", r"C:\Users\YXS\Downloads\t2.png")
    print(tx, ty)
