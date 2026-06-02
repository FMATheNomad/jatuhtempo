import logging
from polar_sdk import Polar
from app.core.config import settings

logger = logging.getLogger(__name__)


def create_checkout_url(telegram_id: int) -> str | None:
    if not settings.polar_access_token:
        logger.warning("POLAR_ACCESS_TOKEN not set")
        return None
    if not settings.polar_product_id:
        logger.warning("POLAR_PRODUCT_ID not set")
        return None

    with Polar(access_token=settings.polar_access_token) as polar:
        res = polar.checkouts.create(request={
            "products": [settings.polar_product_id],
            "success_url": settings.polar_success_url,
            "metadata": {"telegram_id": str(telegram_id)},
        })
        return res.url
