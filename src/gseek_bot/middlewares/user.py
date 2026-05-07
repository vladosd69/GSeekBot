from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Coroutine, Self

from aiogram import BaseMiddleware, Dispatcher
from aiogram.dispatcher.middlewares.data import MiddlewareData
from pydantic import BaseModel

from gseek_bot.database.models.user import UserModel

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from aiogram.types import TelegramObject, Update, User

logger = logging.getLogger(__name__)


@dataclass
class UsersMiddleware(BaseMiddleware):
    tasks: set[asyncio.Task[Any]] = field(default_factory=set)

    @classmethod
    def setup(cls, dp: Dispatcher) -> Self:
        assert not any(isinstance(x, cls) for x in dp.update.outer_middleware._middlewares)
        middleware = cls()
        dp.update.outer_middleware.register(middleware)  # ty:ignore[invalid-argument-type]
        dp["users_middleware"] = middleware
        return middleware

    async def on_shutdown(self) -> None:
        await asyncio.wait(self.tasks.copy())

    @classmethod
    async def create_user(cls, *, user: User) -> tuple[UserModel, bool]:
        is_new = False
        if user.username:
            another_user = await UserModel.find_one(
                UserModel.username == user.username, UserModel.id != user.id
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
        return user_model, is_new

    @classmethod
    def extract_users(cls, event: BaseModel) -> list[User]:
        result = {}

        for field_name in event.__pydantic_fields__:
            buffer = []
            value = getattr(event, field_name)
            if isinstance(value, User):
                buffer += [value]
            elif isinstance(value, BaseModel):
                if extend_buffer := cls.extract_users(value):
                    buffer.extend(extend_buffer)
            for user in buffer:
                result[user.id] = user

        return list(result.values())

    async def save_user(self, user: User) -> None:
        user_model, is_new = await self.create_user(user=user)
        await (user_model.insert if is_new else user_model.save)()

    def create_task[T](self, coro: Coroutine[None, None, T]) -> asyncio.Task[T]:
        task = asyncio.create_task(coro)
        self.tasks.add(task)
        task.add_done_callback(self.tasks.discard)
        return task

    async def save_users(self, event: TelegramObject) -> None:
        for user in self.extract_users(event):
            self.create_task(self.save_user(user))

    async def __call__(
        self,
        handler: Callable[[TelegramObject, MiddlewareData], Awaitable[Any]],
        event: Update,
        data: MiddlewareData,
    ) -> Any:  # ty:ignore[invalid-method-override]
        self.create_task(self.save_users(event))
        return await handler(event, data)
