from datetime import date, datetime

from httpx import AsyncClient, Cookies

BASE_URL = "https://12gksp.medtalon.by"


class ClinicClient:
    def __init__(self) -> None:
        self._client = AsyncClient(base_url=BASE_URL, timeout=15)

    async def __aenter__(self) -> "ClinicClient":
        return self

    async def __aexit__(self, *args) -> None:
        await self._client.aclose()

    async def accept_agreement(self) -> bool:
        resp = await self._client.post("/")
        return resp.is_success

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
                return [t for t in all_talons if t.get("isFree")]
        return []

    def find_doctor_name(self, schedule: list[dict], doctor_id: int) -> str:
        for entry in schedule:
            if entry.get("doctorId") == doctor_id:
                return entry.get("title", "Прием")
        return f"ID {doctor_id}"

    def find_doctor_cabinet(self, schedule: list[dict], doctor_id: int) -> str:
        for entry in schedule:
            if entry.get("doctorId") == doctor_id:
                return entry.get("cabinet") or "не указан"
        return "не указан"
