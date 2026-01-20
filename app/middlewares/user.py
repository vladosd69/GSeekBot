from __future__ import annotations

import logging
from datetime import datetime, UTC
from typing import TYPE_CHECKING, Any, cast
from aiogram import BaseMiddleware

from app.database.models.user import UserModel

if TYPE_CHECKING:
    from aiogram.types import TelegramObject, Update, User
    from collections.abc import Awaitable, Callable

logger = logging.getLogger(__name__)


async def _create_user(*, user: User) -> UserModel:
    is_new = False
    if user.username:
        another_user = await UserModel.find_one(
            UserModel.username == user.username,
            UserModel.id != user.id
        )
        if another_user:
            another_user.username = None
            await another_user.save()

    user_model: UserModel | None = await UserModel.get(user.id)
    if not user_model:
        user_model = UserModel(
            id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            is_telegram_premium=bool(user.is_premium),
        )
        is_new = True
    else:
        user_model.username = user.username
        user_model.first_name = user.first_name
        user_model.last_name = user.last_name
        user_model.is_telegram_premium = bool(user.is_premium)
        user_model.last_active = datetime.now(UTC)
    return cast(UserModel, user_model), is_new


class CheckUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        user_model: UserModel | None = None

        user: User = data.get("event_from_user")

        if TYPE_CHECKING:
            assert isinstance(event, Update)

        match event.event_type:
            case "message" | "business_message":
                if user.is_bot is False:
                    user_model, is_new_user = await _create_user(user=user)

            case (
                "callback_query"
                | "my_chat_member"
                | "chat_member"
                | "inline_query"
                | "chosen_inline_result"
                | "business_connection"
                | "pre_checkout_query"
            ):
                user_model, is_new_user = await _create_user(user=user)

            case _:
                return None

        data["user_model"] = user_model

        result = await handler(event, data)
        if "UNHANDLED" not in str(result) and user_model:
            await (user_model.insert() if is_new_user else user_model.save())
        return result
