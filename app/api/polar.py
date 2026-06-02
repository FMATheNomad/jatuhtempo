import os
import logging

from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from sqlalchemy import select

from app.core.db import async_session_factory
from app.api.debts import get_current_user
from app.models.user import User
from app.services.polar_service import create_checkout_url

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/polar", tags=["polar"])


class CheckoutResponse(BaseModel):
    url: str


@router.get("/checkout")
async def polar_checkout(user: User = Depends(get_current_user)):
    url = create_checkout_url(user.telegram_id)
    if not url:
        raise HTTPException(503, "Polar.sh not configured")
    return CheckoutResponse(url=url)


@router.post("/webhook")
async def polar_webhook(request: Request):
    body = await request.body()
    headers = dict(request.headers)

    secret = os.environ.get("POLAR_WEBHOOK_SECRET", "")
    if secret:
        try:
            from polar_sdk.webhooks import validate_event, WebhookVerificationError
            validate_event(body=body, headers=headers, secret=secret)
        except WebhookVerificationError:
            logger.warning("Invalid webhook signature")
            return "", 403
        except ImportError:
            logger.warning("polar_sdk.webhooks not available, skipping verification")

    import json
    payload = json.loads(body)
    event = payload.get("type", "")

    if event == "order.paid":
        data = payload.get("data", {})
        metadata = data.get("metadata", {})
        telegram_id = metadata.get("telegram_id")
        customer_id = data.get("customer_id") or data.get("customer", {}).get("id")

        if telegram_id:
            async with async_session_factory() as session:
                result = await session.execute(
                    select(User).where(User.telegram_id == int(telegram_id))
                )
                user = result.scalar_one_or_none()
                if user:
                    user.subscription_status = "pro"
                    if customer_id:
                        user.polar_customer_id = str(customer_id)
                    await session.commit()
                    logger.info(f"User {telegram_id} upgraded to pro via order.paid")

    elif event == "subscription.active":
        data = payload.get("data", {})
        metadata = data.get("metadata", {})
        telegram_id = metadata.get("telegram_id")
        customer_id = data.get("customer_id") or data.get("customer", {}).get("id")

        if telegram_id:
            async with async_session_factory() as session:
                result = await session.execute(
                    select(User).where(User.telegram_id == int(telegram_id))
                )
                user = result.scalar_one_or_none()
                if user:
                    user.subscription_status = "pro"
                    if customer_id:
                        user.polar_customer_id = str(customer_id)
                    await session.commit()
                    logger.info(f"User {telegram_id} subscription activated")

    return {"ok": True}
