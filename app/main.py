import asyncio
import logging
from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.memory import SimpleEventIsolation
from aiogram.client.default import DefaultBotProperties
from app.handlers import router
from app.middlewares import register_middlewares
from app.core.config import Settings
from app.core.logger import configure_logging
from app.database import connection

logger = logging.getLogger(__name__)


async def startup(
    dispatcher: Dispatcher,
    settings: Settings,
) -> None:
    await connection.connect_to_mongo(settings)

    register_middlewares(dispatcher)
    dispatcher.include_router(router)

    logger.info("Bot started")


async def shutdown(dispatcher: Dispatcher) -> None: # noqa: ARG001
    logger.info("Bot stopped")


async def main() -> None:
    configure_logging(file_name="bot")
    settings: Settings = Settings()

    bot = Bot(
        token=settings.BOT_TOKEN.get_secret_value(),
        default=DefaultBotProperties(parse_mode="HTML"),
    )

    dispatcher = Dispatcher(
        events_isolation=SimpleEventIsolation(),
        settings=settings,
    )

    dispatcher.startup.register(startup)
    dispatcher.shutdown.register(shutdown)

    await dispatcher.start_polling(bot, allowed_updates=dispatcher.resolve_used_update_types())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Stopped by user")
    except Exception:
        logger.exception("Fatal error")
