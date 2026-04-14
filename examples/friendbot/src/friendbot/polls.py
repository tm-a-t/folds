import random
from pathlib import Path

from telethon import Button, TelegramClient
from telethon.tl import types
from telethon.tl.types import InputMediaPoll

MAX_OPTIONS = 12
ADD_TO_CHAT_BUTTON_TEXT = "Запустить вопросы в чате друзей"


async def build_add_to_chat_button(client: TelegramClient) -> Button:
    bot_info = await client.get_me()
    if not bot_info.username:
        raise ValueError("Bot doesn't have a username O_o")

    return Button.url(
        ADD_TO_CHAT_BUTTON_TEXT,
        f"https://t.me/{bot_info.username}?startgroup=true",
    )


class PollService:
    def __init__(self, question_file: Path):
        self.questions = self._load_questions(question_file)

    def pick_question(self) -> str:
        return random.choice(self.questions)

    async def get_poll_options(self, client, chat_ref: int) -> list[str]:
        names: list[str] = []
        seen: set[str] = set()

        async for participant in client.iter_participants(chat_ref):
            if not isinstance(participant, types.User):
                continue
            if participant.bot or participant.deleted:
                continue

            name = _pick_member_name(participant)
            if name not in seen:
                seen.add(name)
                names.append(name)

        if len(names) < 2:
            raise ValueError("Need at least 2 non-bot members to create a poll.")

        if len(names) > MAX_OPTIONS:
            names = random.sample(names, k=MAX_OPTIONS)

        return names

    async def send_poll(self, client: TelegramClient, chat_ref: int, question: str, options: list[str], button: Button | None) -> None:
        poll_answers = [
            types.PollAnswer(text=types.TextWithEntities(text=option, entities=[]), option=f"{index}".encode("utf-8"))
            for index, option in enumerate(options, start=1)
        ]

        poll = types.Poll(
            id=random.getrandbits(63),
            question=types.TextWithEntities(text=question, entities=[]),
            answers=poll_answers,
            public_voters=True,
            multiple_choice=False,
            quiz=False,
        )

        await client.send_message(chat_ref, file=InputMediaPoll(poll=poll), buttons=button)

    async def send_random_poll(self, client, chat_ref: int, show_ad_button: bool = True) -> None:
        options = await self.get_poll_options(client, chat_ref)
        question = self.pick_question()

        button = await build_add_to_chat_button(client) if show_ad_button else None

        await self.send_poll(client, chat_ref, question, options, button)

    @staticmethod
    def _load_questions(path: Path) -> list[str]:
        if not path.exists():
            raise FileNotFoundError(f"Question file was not found: {path}")

        questions = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if not questions:
            raise ValueError(f"Question file is empty: {path}")
        return questions


def _pick_member_name(user: types.User) -> str:
    full_name = " ".join(part for part in [user.first_name, user.last_name] if part).strip()
    if full_name:
        return full_name
    if user.username:
        return f"@{user.username}"
    return f"Member {user.id}"
