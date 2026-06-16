from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    telegram_bot_token: str
    telegram_chat_id: int
    clinic_base_url: str = "https://12gksp.medtalon.by"
    doctor_ids: str = "1437"
    days_to_scan: int = 5
    check_interval: int = 3600
    state_file_path: str = "state.json"

    @property
    def doctor_id_list(self) -> list[int]:
        return [int(x.strip()) for x in self.doctor_ids.split(",")]


settings = Settings()
