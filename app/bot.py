import logging

from aiogram import Dispatcher, Router, types
from aiogram.filters import Command

from config import settings
from monitor import check_free_slots

router = Router()
log = logging.getLogger(__name__)


def _slot_text(slot: dict) -> str:
    doctor_id = slot.get("_doctor_id", "")
    doctor_name = slot.get("_doctor_name", f"ID {doctor_id}")
    date_str = slot.get("_date", "")
    time_str = slot.get("talonTime", "")
    cabinet = slot.get("_cabinet", "не указан")
    link = (
        f"https://12gksp.medtalon.by/talon"
        f"#/talons/{slot.get('talonDateTime', '')[:10]}/vrach/{doctor_id}/{doctor_name}"
    )
    return (
        f"\U0001f7e2 \u0421\u0432\u043e\u0431\u043e\u0434\u043d\u044b\u0439 \u0442\u0430\u043b\u043e\u043d!\n\n"
        f"\u0412\u0440\u0430\u0447: {doctor_name}\n"
        f"\u041a\u0430\u0431\u0438\u043d\u0435\u0442: {cabinet}\n"
        f"\u0414\u0430\u0442\u0430: {date_str}\n"
        f"\u0412\u0440\u0435\u043c\u044f: {time_str}\n\n"
        f"\u0417\u0430\u043f\u0438\u0441\u044c: {link}"
    )


@router.message(Command("start"))
async def cmd_start(message: types.Message) -> None:
    await message.answer(
        "\u0411\u043e\u0442 \u043c\u043e\u043d\u0438\u0442\u043e\u0440\u0438\u043d\u0433\u0430 \u0441\u0432\u043e\u0431\u043e\u0434\u043d\u044b\u0445 \u0442\u0430\u043b\u043e\u043d\u043e\u0432 \u0432 "
        "12-\u0439 \u0441\u0442\u043e\u043c\u0430\u0442\u043e\u043b\u043e\u0433\u0438\u0447\u0435\u0441\u043a\u043e\u0439 \u043f\u043e\u043b\u0438\u043a\u043b\u0438\u043d\u0438\u043a\u0435.\n\n"
        "\u041a\u043e\u043c\u0430\u043d\u0434\u044b:\n"
        "/status \u2014 \u043f\u0440\u043e\u0432\u0435\u0440\u0438\u0442\u044c \u0441\u0432\u043e\u0431\u043e\u0434\u043d\u044b\u0435 \u0442\u0430\u043b\u043e\u043d\u044b \u0441\u0435\u0439\u0447\u0430\u0441"
    )


@router.message(Command("status"))
async def cmd_status(message: types.Message) -> None:
    await message.answer(
        "\u041f\u0440\u043e\u0432\u0435\u0440\u044f\u044e \u0441\u0432\u043e\u0431\u043e\u0434\u043d\u044b\u0435 \u0442\u0430\u043b\u043e\u043d\u044b..."
    )
    try:
        slots = await check_free_slots()
        if slots:
            for slot in slots:
                await message.answer(_slot_text(slot), disable_web_page_preview=True)
            await message.answer(
                f"\u0412\u0441\u0435\u0433\u043e \u043d\u043e\u0432\u044b\u0445 \u0441\u0432\u043e\u0431\u043e\u0434\u043d\u044b\u0445 \u0442\u0430\u043b\u043e\u043d\u043e\u0432: {len(slots)}"
            )
        else:
            await message.answer(
                "\u0421\u0432\u043e\u0431\u043e\u0434\u043d\u044b\u0445 \u0442\u0430\u043b\u043e\u043d\u043e\u0432 \u043d\u0435\u0442 \u043d\u0430 \u0431\u043b\u0438\u0436\u0430\u0439\u0448\u0438\u0435 \u0434\u043d\u0438."
            )
    except Exception as e:
        log.exception("Status check failed")
        await message.answer(
            f"\u041e\u0448\u0438\u0431\u043a\u0430 \u043f\u0440\u0438 \u043f\u0440\u043e\u0432\u0435\u0440\u043a\u0435: {e}"
        )


async def notify_free_slots(bot: "aiogram.Bot", slots: list[dict]) -> None:
    if not slots:
        return
    for slot in slots:
        await bot.send_message(
            settings.telegram_chat_id,
            _slot_text(slot),
            disable_web_page_preview=True,
        )
    await bot.send_message(
        settings.telegram_chat_id,
        f"\u0412\u0441\u0435\u0433\u043e \u043d\u043e\u0432\u044b\u0445 \u0441\u0432\u043e\u0431\u043e\u0434\u043d\u044b\u0445 \u0442\u0430\u043b\u043e\u043d\u043e\u0432: {len(slots)}",
    )
