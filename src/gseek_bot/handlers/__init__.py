from __future__ import annotations

from aiogram import Router

from . import inline, message

__all__ = [
    "inline",
    "message",
]

router = Router()
router.include_router(message.router)
router.include_router(inline.router)
