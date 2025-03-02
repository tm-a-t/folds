from abc import ABC, abstractmethod

from telethon.events.common import EventCommon

from folds.exceptions import FoldsAdminException


class Admin(ABC):
    @abstractmethod
    async def is_authorized(self, event: EventCommon) -> bool: ...


class EmptyAdmin(Admin):
    async def is_authorized(self, event: EventCommon) -> bool:
        raise FoldsAdminException('Admin configuration is not defined for this app.')


class SimpleAdmin(Admin):
    user_ids: list[int]
    chat_id: int

    def __init__(self, *, user_ids: list[int] | None = None, chat_id: int | None = None):
        self.user_ids = user_ids or []
        self.chat_id = chat_id

    async def is_authorized(self, event: EventCommon) -> bool:
        sender_id = getattr(event, 'sender_id', None)
        return sender_id in self.user_ids or self.chat_id in (event.chat_id, event.chat.id)
