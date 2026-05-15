import logging
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)

_ocr = None


def _get_ocr():
    global _ocr
    if _ocr is None:
        try:
            from paddleocr import PaddleOCR
            _ocr = PaddleOCR(use_angle_cls=True, lang="id", show_log=False)
            logger.info("PaddleOCR initialized")
        except Exception as e:
            logger.error(f"Failed to initialize PaddleOCR: {e}")
            raise
    return _ocr


async def ocr_image(image_path: str | Path) -> str:
    ocr = _get_ocr()
    result = ocr.ocr(str(image_path), cls=True)
    texts = []
    for line_group in result:
        if line_group is None:
            continue
        for line in line_group:
            texts.append(line[1][0])
    return "\n".join(texts)
