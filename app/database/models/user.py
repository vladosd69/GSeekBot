from datetime import UTC, datetime

from beanie import Document, Insert, before_event


class UserModel(Document):
    id: int
    username: str | None = None
    first_name: str
    last_name: str | None = None
    is_telegram_premium: bool = False

    registration_datetime: datetime | None = None
    last_active: datetime | None = None

    class Settings:
        name = "users"
        use_state_management = True

    @before_event(Insert)
    async def set_date(self) -> None:
        now = datetime.now(UTC)
        self.registration_datetime = now
        self.last_active = now
