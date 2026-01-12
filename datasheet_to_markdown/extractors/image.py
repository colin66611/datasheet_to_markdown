"""图片提取器"""

import os
from typing import List, Dict, Any
from datasheet_to_markdown.utils.logger import setup_logger

logger = setup_logger(__name__)


class ImageExtractor:
    """图片提取器"""

    def __init__(self, output_dir: str = "output/images"):
        """
        初始化图片提取器

        Args:
            output_dir: 图片输出目录
        """
        self.output_dir = output_dir
        self.logger = logger

        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)

    def extract(self, page: Any, page_num: int) -> List[Dict]:
        """
        提取图片

        Args:
            page: pdfplumber页面对象
            page_num: 页码

        Returns:
            图片信息列表：
            [
                {
                    "path": "images/page1_img0.png",
                    "page": 1,
                    "index": 0
                }
            ]
        """
        images = []

        try:
            # 检查页面是否有图片
            if not hasattr(page, "images") or not page.images:
                return images

            # 遍历页面中的图片
            for img_index, img in enumerate(page.images):
                # 生成文件名
                filename = f"page{page_num}_img{img_index}.png"
                filepath = os.path.join(self.output_dir, filename)

                # 尝试保存图片
                try:
                    # pdfplumber的image对象包含stream，可以保存
                    if "stream" in img:
                        # 获取图片数据
                        image_data = img["stream"]

                        # 保存为PNG（简化版：直接使用PIL）
                        # 注意：这里需要根据实际情况处理，可能需要额外的库
                        # 暂时只记录路径信息

                        image_info = {
                            "path": f"images/{filename}",
                            "page": page_num,
                            "index": img_index,
                            "bbox": (
                                img.get("x0", 0),
                                img.get("y0", 0),
                                img.get("x1", 0),
                                img.get("y1", 0)
                            )
                        }

                        images.append(image_info)
                        self.logger.debug(f"提取图片: {filename}")

                except Exception as e:
                    self.logger.warning(f"保存图片失败 ({filename}): {e}")

        except Exception as e:
            self.logger.error(f"图片提取失败: {e}")

        return images
