import os
import logging
import json

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


async def send_telegram_notification(telegram_id: int, text: str):
    """
    Отправляет уведомление пользователю в Телеграм бот, если бот активен.
    """
    from app.core.scheduler import _bot_instance
    if _bot_instance:
        try:
            await _bot_instance.send_message(chat_id=telegram_id, text=text)
            logger.info(f"Notification sent to Telegram ID {telegram_id}")
        except Exception as e:
            logger.error(f"Failed to send Telegram notification to {telegram_id}: {e}")
    else:
        logger.warning("Telegram bot instance is not available for notifications")


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

    payload = json.loads(body)
    event = payload.get("type", "")

    # Возможные события, влияющие на получение статуса PRO
    active_events = ["order.paid", "subscription.active", "subscription.created"]
    # События, отменяющие PRO или требующие его аннулирования
    revoke_events = ["subscription.revoked", "subscription.canceled"]

    if event in active_events:
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
                    logger.info(f"User {telegram_id} upgraded to pro via {event}")

    elif event in revoke_events or event == "subscription.updated":
        data = payload.get("data", {})
        metadata = data.get("metadata", {})
        telegram_id = metadata.get("telegram_id")
        
        # Если статус подписки в subscription.updated изменился на canceled или expired
        sub_status = data.get("status")
        is_revoked = event in revoke_events or sub_status in ["canceled", "expired"]

        if is_revoked and telegram_id:
            async with async_session_factory() as session:
                result = await session.execute(
                    select(User).where(User.telegram_id == int(telegram_id))
                )
                user = result.scalar_one_or_none()
                if user and user.subscription_status == "pro":
                    user.subscription_status = "free"
                    await session.commit()
                    logger.info(f"User {telegram_id} downgraded to free tier")
                    
                    # Отправляем уведомление
                    await send_telegram_notification(
                        telegram_id=int(telegram_id),
                        text="<b>Langgananmu telah berakhir</b>\n\nPaket pro Anda telah habis masa berlakunya. Anda telah dikembalikan ke fiktur standar (Free)."
                    )

    return {"ok": True}
