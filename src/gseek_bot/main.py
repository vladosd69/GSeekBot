from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Annotated

import platformdirs
import typer

if TYPE_CHECKING:
    from aiogram import Bot, Dispatcher

    from gseek_bot.core.config import Settings


DEFAULT_LOG_FILE_PATH = Path(platformdirs.user_log_dir("gseek-bot")) / "bot.log"

logger = logging.getLogger(__name__)

cli = typer.Typer(
    rich_markup_mode=None,
    pretty_exceptions_enable=False,
    pretty_exceptions_show_locals=False,
    add_completion=False,
    suggest_commands=False,
    context_settings={
        "help_option_names": ["--help", "-h"],
    },
)


async def startup(
    bots: list[Bot],
    dispatcher: Dispatcher,
    settings: Settings,
) -> None:
    from gseek_bot.database import connection
    from gseek_bot.handlers import router
    from gseek_bot.middlewares import register_middlewares

    await connection.connect_to_mongo(settings)

    bots_info = [await x.get_me() for x in bots]

    register_middlewares(dispatcher)
    dispatcher.include_router(router)

    logger.info(f"Bot started ({', '.join(f'@{x.username}: {x.full_name}' for x in bots_info)})")


async def shutdown() -> None:
    logger.info("Bot stopped")


async def main(settings: Settings, log_file: Path) -> None:
    from aiogram import Bot, Dispatcher
    from aiogram.client.default import DefaultBotProperties
    from aiogram.fsm.storage.memory import SimpleEventIsolation

    from gseek_bot.core.logger import configure_logging

    configure_logging(file_path=log_file)

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


@cli.command()
def run(
    env_file: Annotated[Path | None, typer.Option("--env-file", "-e")] = None,
    log_file: Annotated[Path, typer.Option(envvar="GSEEKBOT_LOG_FILE")] = DEFAULT_LOG_FILE_PATH,
) -> None:
    from pydantic import ValidationError

    from gseek_bot.core.config import Settings

    try:
        log_file.resolve().parent.mkdir(parents=True, exist_ok=True)

        try:
            kw = {}
            if env_file is not None and env_file.exists():
                kw["_env_file"] = env_file

            settings = Settings(**kw)
        except ValidationError as e:
            logger.critical("--- Config validation error ---\n%s", e.__repr__())
            raise typer.Exit(1)  # noqa: B904

        main_coro = main(settings=settings, log_file=log_file)

        try:
            import uvloop
        except ImportError:
            asyncio.run(main_coro)
        else:
            uvloop.run(main_coro)
    except typer.Exit:
        raise
    except KeyboardInterrupt:
        logger.info("Stopped by user")
    except Exception:
        logger.exception("Fatal error")


if __name__ == "__main__":
    cli()
