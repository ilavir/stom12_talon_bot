import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from bot import notify_free_slots, router
from config import settings
from monitor import check_free_slots

log = logging.getLogger(__name__)


async def monitor_loop(bot: Bot) -> None:
    await asyncio.sleep(5)
    while True:
        try:
            slots = await check_free_slots()
            await notify_free_slots(bot, slots)
        except Exception:
            log.exception("Monitor cycle failed")
        await asyncio.sleep(settings.check_interval)


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode="HTML"),
    )
    dp = Dispatcher()
    dp.include_router(router)

    asyncio.create_task(monitor_loop(bot))

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
