"""
Notification dispatch service.

Sends notifications for marketplace events:
- New message received
- New review posted
- Listing marked as sold
"""

from __future__ import annotations

import logging

from app.core.config import notification_config
from app.core.notifications import (
    NotificationProvider,
    ConsoleProvider,
    WhatsAppProvider,
)

logger = logging.getLogger(__name__)

_provider: NotificationProvider | None = None


def get_provider() -> NotificationProvider:
    """Get the active notification provider (singleton, lazy-init)."""
    global _provider
    if _provider is None:
        provider_name = notification_config.provider
        if provider_name == "whatsapp":
            _provider = WhatsAppProvider()
        else:
            _provider = ConsoleProvider()
    return _provider


async def notify_new_message(recipient_phone: str, sender_name: str, listing_title: str) -> bool:
    """Notify a user that they received a new message about a listing."""
    message = f"New message from {sender_name} about '{listing_title}'"
    try:
        return await get_provider().send(recipient_phone, message)
    except Exception:
        logger.exception("Failed to send new message notification")
        return False


async def notify_new_review(recipient_phone: str, reviewer_name: str, rating: int) -> bool:
    """Notify a seller that they received a new review."""
    message = f"New {rating}-star review from {reviewer_name}"
    try:
        return await get_provider().send(recipient_phone, message)
    except Exception:
        logger.exception("Failed to send new review notification")
        return False


async def notify_listing_sold(recipient_phone: str, listing_title: str) -> bool:
    """Notify a seller that their listing was marked as sold."""
    message = f"Your listing '{listing_title}' has been marked as sold"
    try:
        return await get_provider().send(recipient_phone, message)
    except Exception:
        logger.exception("Failed to send listing sold notification")
        return False
