import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from folds import Bot, Message, Skill, SystemMessage
from folds.context import bot as current_bot
from telethon import utils as telethon_utils
from telethon.tl import types

from friendbot.config import Settings, load_settings
from friendbot.polls import PollService, build_add_to_chat_button
from friendbot.storage import GroupStore, KnownGroup

logger = logging.getLogger(__name__)
ADMIN_NOTICE = "Это админ-команда бота. Остальным участникам повторять её не нужно."
INTRO_MESSAGE = "Привет. Каждый день я отправляю вопросик про участников чата."


@dataclass(slots=True)
class FriendbotContext:
    settings: Settings
    poll_service: PollService
    store: GroupStore
    scheduler: AsyncIOScheduler
    known_chat_ids: set[int]


friendbot_skill = Skill()


def _context() -> FriendbotContext:
    return current_bot.app.context


async def resolve_group_info(client, chat_ref: int) -> tuple[int, str | None, str | None]:
    entity = await client.get_entity(chat_ref)
    if not isinstance(entity, (types.Chat, types.Channel)):
        raise ValueError(f"Chat {chat_ref} is not a group/supergroup.")

    chat_id = telethon_utils.get_peer_id(entity)
    title = getattr(entity, "title", None)
    username = getattr(entity, "username", None)
    return chat_id, title, username


async def remember_group(client, store: GroupStore, chat_ref: int) -> tuple[int, bool]:
    chat_id, title, username = await resolve_group_info(client, chat_ref)
    is_new_group = await store.upsert_group(chat_id=chat_id, title=title, username=username)
    return chat_id, is_new_group


def _render_groups(groups: list[KnownGroup]) -> str:
    if not groups:
        return "В базе пока нет известных групп."

    lines = ["Известные группы:"]
    for group in groups:
        parts = [f"- {group.title or '(без названия)'}", f"id={group.chat_id}"]
        if group.username:
            parts.append(f"@{group.username}")
        parts.append(f"last_seen={group.last_seen_at}")
        lines.append(", ".join(parts))

    return "\n".join(lines)


def _is_admin(message: Message) -> bool:
    sender_id = message.sender_id
    return sender_id is not None and sender_id in _context().settings.admin_user_ids


async def _respond_admin_only(message: Message, text: str | None = None):
    if text:
        await message.reply(text)
    if message.is_group:
        await message.reply(ADMIN_NOTICE)


async def _reply_with_add_to_chat_button(message: Message) -> None:
    await message.reply(
        "Добавь меня в чатик друзей, чтобы получать вопросы про друзей.",
        buttons=await build_add_to_chat_button(current_bot),
    )


def _is_start_command(message: Message) -> bool:
    if not message.raw_text:
        return False

    first_word = message.raw_text.split(maxsplit=1)[0].lower()
    if first_word == "/start":
        return True

    bot_username = getattr(current_bot.me, "username", None)
    if not bot_username:
        return False

    return first_word == f"/start@{bot_username.lower()}"


@asynccontextmanager
async def lifespan(app):
    context: FriendbotContext = app.context

    try:
        context.known_chat_ids.clear()
        context.known_chat_ids.update(await context.store.list_chat_ids())
        context.scheduler.start()
        logger.info(
            "Bot started. Daily polls scheduled at %s:%s (%s). Known groups: %s",
            context.settings.poll_hour,
            context.settings.poll_minute,
            context.settings.poll_timezone,
            sorted(context.known_chat_ids),
        )
        yield
    finally:
        if context.scheduler.running:
            context.scheduler.shutdown(wait=False)
        await context.store.close()


async def publish_daily_polls(bot: Bot) -> None:
    context = bot.app.context
    chat_ids = await context.store.list_chat_ids()
    if not chat_ids:
        logger.info("No known groups yet. Add bot to a group and send a message there.")
        return

    for chat_id in chat_ids:
        try:
            await context.poll_service.send_random_poll(bot, chat_id)
            logger.info("Sent poll to %s", chat_id)
        except Exception:
            logger.exception("Failed to send poll to %s", chat_id)


@friendbot_skill.added_to_group
async def on_added(event: SystemMessage):
    context = _context()

    try:
        chat_id, _ = await remember_group(current_bot, context.store, event.chat_id)
        context.known_chat_ids.add(chat_id)
        logger.info("Bot added to group %s", chat_id)
        await event.respond(INTRO_MESSAGE)
        await context.poll_service.send_random_poll(current_bot, chat_id, show_ad_button=False)
    except Exception:
        logger.exception("Failed to save newly added group %s", event.chat_id)


@friendbot_skill.group_message
async def on_group_message(message: Message):
    context = _context()
    if message.chat_id in context.known_chat_ids:
        return

    try:
        chat_id, is_new_group = await remember_group(current_bot, context.store, message.chat_id)
        context.known_chat_ids.add(chat_id)
        logger.info("Discovered and saved group %s", chat_id)
        if is_new_group and _is_start_command(message):
            await message.reply(INTRO_MESSAGE)
    except Exception:
        logger.exception("Failed to save discovered group %s", message.chat_id)


@friendbot_skill.group_commands.ask
async def ask(message: Message):
    context = _context()
    if not _is_admin(message):
        await message.reply("Эта команда только для админов бота.")
        return

    try:
        chat_id, _ = await remember_group(current_bot, context.store, message.chat_id)
        context.known_chat_ids.add(chat_id)
        await context.poll_service.send_random_poll(current_bot, chat_id)
        await _respond_admin_only(message)
    except Exception as exc:
        logger.exception("Manual ask failed for chat %s", message.chat_id)
        await _respond_admin_only(message, f"Не удалось отправить опрос: {exc}")


@friendbot_skill.private_commands.groups
async def admin_groups_private(message: Message):
    if not _is_admin(message):
        await message.reply("Эта команда только для админов бота.")
        return

    await _respond_admin_only(message, _render_groups(await _context().store.list_groups()))


@friendbot_skill.private_message
async def on_private_message(message: Message):
    if message.raw_text and message.raw_text.startswith("/"):
        return

    await _reply_with_add_to_chat_button(message)


@friendbot_skill.group_commands.groups
async def admin_groups_group(message: Message):
    if not _is_admin(message):
        await message.reply("Эта команда только для админов бота.")
        return

    await _respond_admin_only(message, _render_groups(await _context().store.list_groups()))


@friendbot_skill.private_commands.start
async def start_private(message: Message):
    await _reply_with_add_to_chat_button(message)


def create_bot(settings: Settings) -> Bot[FriendbotContext]:
    context = FriendbotContext(
        settings=settings,
        poll_service=PollService(settings.question_file),
        store=GroupStore(settings.groups_db_path),
        scheduler=AsyncIOScheduler(timezone=settings.poll_timezone),
        known_chat_ids=set(),
    )
    bot = Bot(context=context, lifespan=lifespan)
    bot.use(friendbot_skill)
    context.scheduler.add_job(
        publish_daily_polls,
        args=[bot],
        trigger="cron",
        hour=settings.poll_hour,
        minute=settings.poll_minute,
    )
    return bot


def main():
    load_dotenv()
    settings = load_settings()

    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )

    create_bot(settings).run()


if __name__ == "__main__":
    main()
