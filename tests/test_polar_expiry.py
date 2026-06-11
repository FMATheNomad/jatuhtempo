import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from app.api.polar import polar_webhook

@pytest.mark.asyncio
async def test_polar_webhook_subscription_unsubscribed():
    """
    Test handling of subscription cancellation/expiry.
    Verify that when subscription.canceled is received, the user status is set to free with notifications.
    """
    mock_user = MagicMock()
    mock_user.telegram_id = 999
    mock_user.subscription_status = "pro"
    mock_user.polar_customer_id = "cust_123"

    mock_scalar = MagicMock()
    # Обрати внимание! Ошибка была в том, что в SqlAlchemy асинхронные вызовы возвращают специальный объект,
    # и scalar_one_or_none должен отдавать реальный объект, но контекст менеджера (async with) требует 
    # асинхронных моков на сессию. Давай сделаем Session полностью AsyncMock
    mock_scalar.scalar_one_or_none = MagicMock(return_value=mock_user)

    mock_session = MagicMock()
    # Мокаем асинхронный контекстный менеджер (async with async_session_factory() as session)
    mock_session.execute = AsyncMock(return_value=mock_scalar)
    mock_session.commit = AsyncMock()

    # Заставим async_session_factory возвращать контекст-менеджер с нашим mock_session
    class AsyncContextManagerMock:
        async def __aenter__(self):
            return mock_session
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    # Симулируем тело запроса для canceled
    payload = {
        "type": "subscription.canceled",
        "data": {
            "id": "sub_123",
            "customer_id": "cust_123",
            "status": "canceled",
            "metadata": {
                "telegram_id": "999"
            }
        }
    }

    class MockRequest:
        async def body(self):
            return json.dumps(payload).encode()
        @property
        def headers(self):
            return {}

    # Мокаем бота тоже
    mock_bot = AsyncMock()
    
    with patch("app.api.polar.async_session_factory", return_value=AsyncContextManagerMock()), \
         patch("app.api.polar.os.environ.get", return_value=""), \
         patch("app.core.scheduler._bot_instance", mock_bot):
        
        req = MockRequest()
        response = await polar_webhook(req)
        assert response == {"ok": True}
        
        # Проверяем, что статус стал free
        assert mock_user.subscription_status == "free"
        # Проверяем, что ушел вызов отправки уведомления в бот
        mock_bot.send_message.assert_called_once_with(
            chat_id=999,
            text="<b>Langgananmu telah berakhir</b>\n\nPaket pro Anda telah habis masa berlakunya. Anda telah dikembalikan ke fiktur standar (Free)."
        )
