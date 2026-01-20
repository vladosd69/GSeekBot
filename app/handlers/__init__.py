from aiogram import Router

from . import message, inline


__all__ = [
    "inline",
    "message",
]

router = Router()
router.include_router(message.router)
router.include_router(inline.router)
