import asyncio
import logging
from pathlib import Path

import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)


async def ocr_image(image_path: str | Path) -> str:
    image = Image.open(image_path)
    text = await asyncio.to_thread(pytesseract.image_to_string, image, lang="ind+eng")
    return text.strip()
