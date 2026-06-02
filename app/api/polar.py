import os
import logging

from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel

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
    payload = await request.json()
    event = payload.get("type", "")

    if event == "checkout.created":
        metadata = payload.get("data", {}).get("metadata", {})
        telegram_id = metadata.get("telegram_id")
        if telegram_id:
            async with async_session_factory() as session:
                from sqlalchemy import select
                result = await session.execute(
                    select(User).where(User.telegram_id == int(telegram_id))
                )
                user = result.scalar_one_or_none()
                if user:
                    logger.info(f"User {telegram_id} completed checkout")
                    # TODO: set subscription status when Polar integration is complete

    elif event == "subscription.active":
        metadata = payload.get("data", {}).get("metadata", {})
        telegram_id = metadata.get("telegram_id")
        if telegram_id:
            async with async_session_factory() as session:
                from sqlalchemy import select
                result = await session.execute(
                    select(User).where(User.telegram_id == int(telegram_id))
                )
                user = result.scalar_one_or_none()
                if user:
                    logger.info(f"Subscription activated for user {telegram_id}")

    return {"ok": True}
