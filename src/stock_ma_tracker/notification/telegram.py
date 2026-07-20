"""Telegram notification delivery."""

from __future__ import annotations

from typing import Any

import requests


class NotificationError(RuntimeError):
    """Raised when a notification cannot be delivered."""


class TelegramNotifier:
    """Send text messages through the Telegram Bot API."""

    def __init__(
        self,
        *,
        bot_token: str,
        chat_id: str,
        timeout_seconds: float = 10.0,
    ) -> None:
        normalized_token = bot_token.strip()
        normalized_chat_id = chat_id.strip()

        if not normalized_token:
            raise ValueError("bot_token must not be empty")

        if not normalized_chat_id:
            raise ValueError("chat_id must not be empty")

        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than zero")

        self._bot_token = normalized_token
        self._chat_id = normalized_chat_id
        self._timeout_seconds = timeout_seconds

    def send(self, message: str) -> None:
        """Send one Telegram text message."""
        normalized_message = message.strip()

        if not normalized_message:
            raise ValueError("message must not be empty")

        url = f"https://api.telegram.org/bot{self._bot_token}/sendMessage"

        payload: dict[str, Any] = {
            "chat_id": self._chat_id,
            "text": normalized_message,
        }

        try:
            response = requests.post(
                url,
                json=payload,
                timeout=self._timeout_seconds,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise NotificationError("failed to send Telegram notification") from exc
