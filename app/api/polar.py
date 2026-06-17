import os
import json
import logging

from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from sqlalchemy import select

from polar_sdk.webhooks import validate_event, WebhookVerificationError

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
            validate_event(body=body, headers=headers, secret=secret)
        except WebhookVerificationError:
            logger.warning("Invalid webhook signature")
            return "", 403

    payload = json.loads(body)
    event = payload.get("type", "")
    data = payload.get("data", {})
    metadata = data.get("metadata", {})
    telegram_id = metadata.get("telegram_id")
    customer_id = data.get("customer_id") or data.get("customer", {}).get("id")

    async with async_session_factory() as session:
        user = None
        if telegram_id:
            result = await session.execute(
                select(User).where(User.telegram_id == int(telegram_id))
            )
            user = result.scalar_one_or_none()
        if not user and customer_id:
            result = await session.execute(
                select(User).where(User.polar_customer_id == str(customer_id))
            )
            user = result.scalar_one_or_none()

        if event == "order.paid":
            if user:
                user.subscription_status = "pro"
                if customer_id:
                    user.polar_customer_id = str(customer_id)
                await session.commit()
                logger.info(f"User upgraded to pro via order.paid: {user.id}")

        elif event == "subscription.active":
            if user:
                user.subscription_status = "pro"
                if customer_id:
                    user.polar_customer_id = str(customer_id)
                await session.commit()
                logger.info(f"Subscription activated: {user.id}")

        elif event in ("subscription.canceled", "subscription.revoked"):
            if user:
                user.subscription_status = "free"
                user.polar_customer_id = None
                await session.commit()
                logger.info(f"Subscription {event}: {user.id}")

        elif event == "order.refunded":
            if user:
                user.subscription_status = "free"
                user.polar_customer_id = None
                await session.commit()
                logger.info(f"Order refunded, user downgraded: {user.id}")

    return {"ok": True}
