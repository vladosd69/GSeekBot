from __future__ import annotations

from typing import TYPE_CHECKING

from gseek_bot.middlewares.user import UsersMiddleware

from . import user

if TYPE_CHECKING:
    from aiogram import Dispatcher

__all__ = ["user"]


def register_middlewares(dispatcher: Dispatcher) -> None:
    UsersMiddleware.setup(dispatcher)
