from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import numpy as np
from ...tools.utils import Padding, Region, get_h_w_c


class SelectMode(Enum):
    ALL_SECTIONS = 1
    CENTER_SECTION = 2
    LARGEST_SECTION = 3


def crop_border_node(
    img: np.ndarray, tolerance: float, select: SelectMode, padding: int
) -> np.ndarray:
    tolerance /= 100

    h, w, c = get_h_w_c(img)

    # find the border color of the border
    border_color = get_border_color(img)

    # figure out which pixels are likely part of the border
    diff: np.ndarray = np.abs(img - border_color)
    if c > 1:
        # make grayscale
        diff = np.mean(diff, axis=-1)
    is_content = diff > tolerance

    # get crop region crop bounds
    crop = get_crop_region(is_content, select)
    crop = crop.add_padding(Padding.all(padding))
    crop = crop.intersect(Region(0, 0, w, h))

    return crop.read_from(img)


def get_crop_region(is_content: np.ndarray, select: SelectMode) -> Region:
    assert is_content.ndim == 2

    # 1. crop horizontally
    is_content_horizontal = np.any(is_content, axis=0)
    section_w = get_inner_section(is_content_horizontal, select)
    is_content = is_content[:, section_w.start : section_w.end]

    # 2. crop vertically
    is_content_vertical = np.any(is_content, axis=1)
    section_h = get_inner_section(is_content_vertical, select)
    is_content = is_content[section_h.start : section_h.end, :]

    crop = Region(
        section_w.start,
        section_h.start,
        section_w.length,
        section_h.length,
    )

    if select != SelectMode.ALL_SECTIONS:
        # 3. crop horizontally again to remove any remaining border
        is_content_horizontal = np.any(is_content, axis=0)
        section_w = get_inner_section(is_content_horizontal, SelectMode.ALL_SECTIONS)
        crop = Region(
            crop.x + section_w.start,
            crop.y,
            section_w.length,
            crop.height,
        )

    return crop


def get_border_color(img: np.ndarray):
    """
    Returns the median color in the 1px border of the image.
    """
    # Get the 1px border of the image
    top = img[0, :, ...]
    bottom = img[-1, :, ...]
    left = img[:, 0, ...]
    right = img[:, -1, ...]
    border = np.concatenate((top, bottom, left, right), axis=0)
    # Get the median color
    return np.median(border, axis=0)


@dataclass(frozen=True)
class Section:
    start: int
    end: int

    @property
    def length(self) -> int:
        return self.end - self.start

    def union(self, other: Section) -> Section:
        return Section(min(self.start, other.start), max(self.end, other.end))

    def distance_to(self, index: int) -> int:
        if index < self.start:
            return self.start - index
        if index >= self.end:
            return index - self.end
        return 0


def get_inner_section(is_content: np.ndarray, select: SelectMode) -> Section:
    assert is_content.ndim == 1
    size = len(is_content)

    # find all content sections in the image
    sections: list[Section] = []
    start = None
    for i in range(size):
        if not is_content[i]:
            if start is not None:
                sections.append(Section(start, i))
                start = None
        elif start is None:
            start = i
    if start is not None:
        sections.append(Section(start, size))
        start = None
    if len(sections) == 0:
        return Section(0, size)

    # select the relevant section
    if select == SelectMode.ALL_SECTIONS:
        return sections[0].union(sections[-1])
    if select == SelectMode.CENTER_SECTION:
        distances = [section.distance_to(size // 2) for section in sections]
        return sections[np.argmin(distances)]
    if select == SelectMode.LARGEST_SECTION:
        return max(sections, key=lambda section: section.length)
