import logging
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import Settings
from .models import user

logger = logging.getLogger(__name__)


async def connect_to_mongo(settings: Settings) -> None:
    client = AsyncIOMotorClient(settings.mongo_dsn)
    db = client[settings.MONGO.NAME]
    await init_beanie(
        database=db,
        document_models=[
            user.UserModel,
        ]
    )

    logger.info("Connected to MongoDB")
