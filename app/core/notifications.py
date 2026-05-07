"""
Notification provider abstraction for sending alerts via WhatsApp, email, etc.

Uses a provider pattern so the actual notification channel (console, WhatsApp, etc.)
can be swapped without changing business logic.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class NotificationProvider(ABC):
    """Abstract base for all notification backends."""

    @abstractmethod
    async def send(self, to: str, message: str) -> bool:
        """Send a notification. Returns True on success."""
        ...


class ConsoleProvider(NotificationProvider):
    """Dev provider - logs notifications instead of sending them."""

    async def send(self, to: str, message: str) -> bool:
        logger.info("[NOTIFICATION] To: %s | %s", to, message)
        print(f"[NOTIFICATION] To: {to} | {message}")
        return True


class WhatsAppProvider(NotificationProvider):
    """Production provider - sends notifications via WhatsApp Business API.

    Requires WHATSAPP_TOKEN, WHATSAPP_PHONE_NUMBER_ID, and
    WHATSAPP_TEMPLATE_NAME environment variables.

    TODO: Implement when WhatsApp Business API credentials are available.
    """

    def __init__(self) -> None:
        from app.core.config import whatsapp_config

        self.token = whatsapp_config.token
        self.phone_number_id = whatsapp_config.phone_number_id
        self.template_name = whatsapp_config.template_name

    async def send(self, to: str, message: str) -> bool:
        """Send a WhatsApp message via the Business Cloud API."""
        if not self.token or not self.phone_number_id:
            logger.warning("WhatsApp credentials not configured - notification skipped")
            return False

        # TODO: Implement actual API call when credentials are available.
        # import httpx
        # async with httpx.AsyncClient() as client:
        #     resp = await client.post(
        #         f"https://graph.facebook.com/v18.0/{self.phone_number_id}/messages",
        #         headers={"Authorization": f"Bearer {self.token}"},
        #         json={
        #             "messaging_product": "whatsapp",
        #             "to": to,
        #             "type": "template",
        #             "template": {
        #                 "name": self.template_name,
        #                 "language": {"code": "en"},
        #                 "components": [
        #                     {
        #                         "type": "body",
        #                         "parameters": [{"type": "text", "text": message}],
        #                     }
        #                 ],
        #             },
        #         },
        #     )
        #     return resp.status_code == 200

        logger.info("[WHATSAPP STUB] Would send to %s: %s", to, message)
        return True
