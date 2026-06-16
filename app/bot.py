from __future__ import annotations

import logging

from aiogram import Bot, Router, types
from aiogram.filters import Command
from config import settings
from monitor import check_free_slots

router = Router()
log = logging.getLogger(__name__)


def _booking_label(bt: str) -> str:
    if bt == "online":
        return "онлайн"
    if bt == "registry":
        return "в регистратуре"
    return bt


def _slot_text(slot: dict) -> str:
    doctor_id = slot.get("_doctor_id", "")
    doctor_name = slot.get("_doctor_name", f"ID {doctor_id}")
    doctor_translit = slot.get("_doctor_translit", str(doctor_id))
    date_str = slot.get("_date", "")
    time_str = slot.get("talonTime", "")
    cabinet = slot.get("_cabinet", "не указан")
    booking_type = _booking_label(slot.get("_booking_type", ""))
    link = (
        f"{settings.clinic_base_url}/talon"
        f"#/talons/{slot.get('talonDateTime', '')[:10]}/vrach/{doctor_id}/{doctor_translit}"
    )
    return (
        f"🟢 Свободный талон!\n\n"
        f"Врач: {doctor_name}\n"
        f"Кабинет: {cabinet}\n"
        f"Дата: {date_str}\n"
        f"Время: {time_str}\n"
        f"Доступен: {booking_type}\n\n"
        f"Запись: {link}"
    )


@router.message(Command("start"))
async def cmd_start(message: types.Message) -> None:
    await message.answer(
        "Бот мониторинга свободных талонов в "
        "12-й стоматологической поликлинике.\n\n"
        "Команды:\n"
        "/status — проверить свободные талоны сейчас"
    )


@router.message(Command("status"))
async def cmd_status(message: types.Message) -> None:
    await message.answer("Проверяю свободные талоны...")
    try:
        slots = await check_free_slots()
        if slots:
            for slot in slots:
                await message.answer(_slot_text(slot), disable_web_page_preview=True)
            await message.answer(f"Всего новых свободных талонов: {len(slots)}")
        else:
            await message.answer("Свободных талонов нет на ближайшие дни.")
    except Exception as e:
        log.exception("Status check failed")
        await message.answer(f"Ошибка при проверке: {e}")


async def notify_free_slots(bot: Bot, slots: list[dict]) -> None:
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
        f"Всего новых свободных талонов: {len(slots)}",
    )
