"""Tests for notification factory functions."""

from __future__ import annotations

import pytest

from stock_ma_tracker.application import (
    create_telegram_notifier,
)
from stock_ma_tracker.notification import TelegramNotifier


def test_create_telegram_notifier_from_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "TELEGRAM_BOT_TOKEN",
        "test-token",
    )
    monkeypatch.setenv(
        "TELEGRAM_CHAT_ID",
        "123456",
    )

    notifier = create_telegram_notifier()

    assert isinstance(notifier, TelegramNotifier)


def test_create_telegram_notifier_requires_bot_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(
        "TELEGRAM_BOT_TOKEN",
        raising=False,
    )
    monkeypatch.setenv(
        "TELEGRAM_CHAT_ID",
        "123456",
    )

    with pytest.raises(
        ValueError,
        match=("TELEGRAM_BOT_TOKEN environment variable is required"),
    ):
        create_telegram_notifier()


def test_create_telegram_notifier_requires_chat_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "TELEGRAM_BOT_TOKEN",
        "test-token",
    )
    monkeypatch.delenv(
        "TELEGRAM_CHAT_ID",
        raising=False,
    )

    with pytest.raises(
        ValueError,
        match=("TELEGRAM_CHAT_ID environment variable is required"),
    ):
        create_telegram_notifier()
