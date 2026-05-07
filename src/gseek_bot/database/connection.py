from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from .models import user

if TYPE_CHECKING:
    from gseek_bot.core.config import Settings

logger = logging.getLogger(__name__)


async def connect_to_mongo(settings: Settings) -> None:
    client = AsyncIOMotorClient(settings.mongo_dsn)
    db = client[settings.MONGO.NAME]
    await init_beanie(
        database=db,  # ty:ignore[invalid-argument-type]
        document_models=[
            user.UserModel,
        ],
    )

    logger.info("Connected to MongoDB")
