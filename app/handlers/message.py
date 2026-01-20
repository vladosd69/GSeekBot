from __future__ import annotations

from aiogram import Router
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aiogram.types import Message

router = Router()


@router.message()
async def handler(message: Message) -> None:
    if message.via_bot:
        return

    blog = '<a href="https://t.me/qublog">Blog</a>'
    github = '<a href="https://github.com/klaymov/GSeekBot">GitHub Repository</a>'

    message_text = "Use @GSeekBot in any chat to search for information on Internet."
    message_text += "\n\nFor example: <code>@GSeekBot What is a metaphor?</code>"
    message_text += f"\n\n{blog} | {github}"

    await message.answer(
        text=message_text,
        disable_web_page_preview=True
    )
