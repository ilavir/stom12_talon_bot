from datetime import date

from config import settings
from httpx import AsyncClient


class ClinicClient:
    def __init__(self) -> None:
        self._client = AsyncClient(base_url=settings.clinic_base_url, timeout=15)
        self._doctors: dict[int, dict] | None = None

    async def __aenter__(self) -> ClinicClient:
        return self

    async def __aexit__(self, *args) -> None:
        await self._client.aclose()

    async def accept_agreement(self) -> bool:
        resp = await self._client.post("/")
        return resp.is_success

    async def _load_doctors(self) -> dict[int, dict]:
        resp = await self._client.get("/api/doctors")
        if resp.status_code == 401:
            await self.accept_agreement()
            resp = await self._client.get("/api/doctors")
        doctors: dict[int, dict] = {}
        if resp.is_success:
            for d in resp.json():
                doctors[d["id"]] = d
        self._doctors = doctors
        return doctors

    async def get_schedule(self, day: date) -> list[dict] | None:
        date_str = day.strftime("%d.%m.%Y")
        resp = await self._client.get(f"/api/talonbriefs/{date_str}")
        if resp.status_code == 401:
            await self.accept_agreement()
            resp = await self._client.get(f"/api/talonbriefs/{date_str}")
        if resp.is_error or resp.text in ("null", ""):
            return None
        return resp.json()

    def find_free_slots(self, schedule: list[dict], doctor_id: int) -> list[dict]:
        for entry in schedule:
            if entry.get("doctorId") == doctor_id:
                if not entry.get("hasFree"):
                    return []
                all_talons = (
                    entry.get("morningTalonTimes", [])
                    + entry.get("afternoonTalonTimes", [])
                    + entry.get("eveningTalonTimes", [])
                )
                slots = []
                for t in all_talons:
                    if t.get("isFree"):
                        t["_booking_type"] = "online"
                        slots.append(t)
                    elif t.get("status") == "openedregistry":
                        t["_booking_type"] = "registry"
                        slots.append(t)
                return slots
        return []

    async def find_doctor_name(self, doctor_id: int) -> str:
        if self._doctors is None:
            await self._load_doctors()
        doc = self._doctors.get(doctor_id) if self._doctors else None
        if doc:
            return f"{doc['lastName']} {doc['firstName']} {doc['secondName']}"
        return f"ID {doctor_id}"

    async def find_doctor_cabinet(self, doctor_id: int) -> str:
        if self._doctors is None:
            await self._load_doctors()
        doc = self._doctors.get(doctor_id) if self._doctors else None
        if doc and doc.get("cabinet"):
            return doc["cabinet"]
        return "не указан"

    async def find_doctor_translit(self, doctor_id: int) -> str:
        if self._doctors is None:
            await self._load_doctors()
        doc = self._doctors.get(doctor_id) if self._doctors else None
        if doc and doc.get("translit"):
            return doc["translit"]
        return str(doctor_id)
