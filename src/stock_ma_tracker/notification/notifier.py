"""Notification delivery abstraction."""

from __future__ import annotations

from typing import Protocol


class Notifier(Protocol):
    """Deliver notification messages."""

    def send(self, message: str) -> None:
        """Send one notification message."""
