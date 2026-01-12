"""Image Extractor"""

import os
from typing import List, Dict, Any
from datasheet_to_markdown.utils.logger import setup_logger

logger = setup_logger(__name__)


class ImageExtractor:
    """Image Extractor"""

    def __init__(self, output_dir: str = "output/images"):
        """
        Initialize image extractor

        Args:
            output_dir: image output directory
        """
        self.output_dir = output_dir
        self.logger = logger

        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)

    def extract(self, page: Any, page_num: int) -> List[Dict]:
        """
        Extract images

        Args:
            page: pdfplumber page object
            page_num: page number

        Returns:
            List of image information:
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
            # Check if page has images
            if not hasattr(page, "images") or not page.images:
                return images

            # Iterate through images on page
            for img_index, img in enumerate(page.images):
                # Generate filename
                filename = f"page{page_num}_img{img_index}.png"
                filepath = os.path.join(self.output_dir, filename)

                # Try to save image
                try:
                    # pdfplumber's image object contains stream, can be saved
                    if "stream" in img:
                        # Get image data
                        image_data = img["stream"]

                        # Save as PNG (simplified version: use PIL directly)
                        # Note: This needs to be handled based on actual situation, may require additional libraries
                        # For now, just record path information

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
                        self.logger.debug(f"Extracted image: {filename}")

                except Exception as e:
                    self.logger.warning(f"Failed to save image ({filename}): {e}")

        except Exception as e:
            self.logger.error(f"Image extraction failed: {e}")

        return images
