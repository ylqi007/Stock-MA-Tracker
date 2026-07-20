from __future__ import annotations

from typing import Any

import pytest
import requests

from stock_ma_tracker.notification import (
    NotificationError,
    TelegramNotifier,
)


class FakeResponse:
    def __init__(
        self,
        error: requests.RequestException | None = None,
    ) -> None:
        self._error = error

    def raise_for_status(self) -> None:
        if self._error is not None:
            raise self._error


def test_send_posts_message_to_telegram(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_post(
        url: str,
        *,
        json: dict[str, Any],
        timeout: float,
    ) -> FakeResponse:
        captured["url"] = url
        captured["json"] = json
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr(
        "stock_ma_tracker.notification.telegram.requests.post",
        fake_post,
    )

    notifier = TelegramNotifier(
        bot_token="test-token",
        chat_id="123456",
        timeout_seconds=5.0,
    )

    notifier.send("Strategy changed")

    assert captured["url"] == ("https://api.telegram.org/bottest-token/sendMessage")
    assert captured["json"] == {
        "chat_id": "123456",
        "text": "Strategy changed",
    }
    assert captured["timeout"] == 5.0


def test_send_raises_notification_error_when_request_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_post(
        url: str,
        *,
        json: dict[str, Any],
        timeout: float,
    ) -> FakeResponse:
        raise requests.ConnectionError("network unavailable")

    monkeypatch.setattr(
        "stock_ma_tracker.notification.telegram.requests.post",
        fake_post,
    )

    notifier = TelegramNotifier(
        bot_token="test-token",
        chat_id="123456",
    )

    with pytest.raises(
        NotificationError,
        match="failed to send Telegram notification",
    ):
        notifier.send("Strategy changed")


@pytest.mark.parametrize(
    ("bot_token", "chat_id", "expected_message"),
    [
        ("", "123456", "bot_token must not be empty"),
        ("test-token", "", "chat_id must not be empty"),
    ],
)
def test_init_rejects_missing_credentials(
    bot_token: str,
    chat_id: str,
    expected_message: str,
) -> None:
    with pytest.raises(ValueError, match=expected_message):
        TelegramNotifier(
            bot_token=bot_token,
            chat_id=chat_id,
        )


def test_send_rejects_empty_message() -> None:
    notifier = TelegramNotifier(
        bot_token="test-token",
        chat_id="123456",
    )

    with pytest.raises(
        ValueError,
        match="message must not be empty",
    ):
        notifier.send("   ")
