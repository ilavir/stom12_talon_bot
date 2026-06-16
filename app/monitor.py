import json
import logging
from datetime import date, datetime, timedelta
from pathlib import Path

from config import settings
from clinic_api import ClinicClient

STATE_FILE = Path("/app/data/state.json")
log = logging.getLogger(__name__)


def _load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"notified_slots": {}}


def _save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False))


def _dates_to_check() -> list[date]:
    today = date.today()
    return [today + timedelta(days=i) for i in range(settings.days_to_scan)]


def _slot_key(slot: dict) -> str:
    return slot.get("talonDateTime", "")


async def check_free_slots() -> list[dict]:
    state = _load_state()
    new_slots: list[dict] = []

    async with ClinicClient() as clinic:
        for day in _dates_to_check():
            schedule = await clinic.get_schedule(day)
            if not schedule:
                continue

            for doctor_id in settings.doctor_id_list:
                free = clinic.find_free_slots(schedule, doctor_id)
                previously = set(state["notified_slots"].get(str(doctor_id), []))

                for slot in free:
                    key = _slot_key(slot)
                    if key and key not in previously:
                        slot["_doctor_id"] = doctor_id
                        slot["_doctor_name"] = clinic.find_doctor_name(
                            schedule, doctor_id
                        )
                        slot["_cabinet"] = clinic.find_doctor_cabinet(
                            schedule, doctor_id
                        )
                        slot["_date"] = day.strftime("%d.%m.%Y")
                        new_slots.append(slot)

    for slot in new_slots:
        doc_id = str(slot["_doctor_id"])
        state["notified_slots"].setdefault(doc_id, [])
        state["notified_slots"][doc_id].append(_slot_key(slot))

    _save_state(state)
    return new_slots
