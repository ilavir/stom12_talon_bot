from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    telegram_bot_token: str
    telegram_chat_id: int
    doctor_ids: str = "1437"
    days_to_scan: int = 5
    check_interval: int = 3600

    @property
    def doctor_id_list(self) -> list[int]:
        return [int(x.strip()) for x in self.doctor_ids.split(",")]


settings = Settings()
