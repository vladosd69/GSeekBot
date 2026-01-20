from aiogram import Dispatcher

from . import user

__all__ = [
    "user",
]

def register_middlewares(dispatcher: Dispatcher) -> None:
    dispatcher.update.outer_middleware(user.CheckUserMiddleware())
