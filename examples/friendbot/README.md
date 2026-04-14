# friendbot

Telegram bot for friend group chats.
It posts a daily "who is most likely..." poll with current chat members as answer options.

## Stack

- [folds](https://papercraft.tmat.me/folds/)
- `apscheduler`
- `uv` for dependency + run management

## Setup

```bash
cd examples/friendbot
uv sync
cp .env.example .env
```

Fill in `.env` values.

## Run

```bash
uv run friendbot
```

## Behavior

- When the bot is added to a group, it sends an intro message and saves that group to SQLite (`groups.sqlite` by default).
- If Telegram misses the add-to-group event, sending `/start` in a group also saves that group and sends the intro message on first discovery.
- Every day at `POLL_HOUR:POLL_MINUTE` (`POLL_TIMEZONE`), bot sends one poll to each saved group.
- Poll options are built from non-bot chat members.
- If there are more than 10 members, 10 random members are used (Telegram poll limit).
- Questions are loaded from [`questions.txt`](questions.txt).
- In private chat, `/start` and regular direct messages show an "Add to chat" button.
- Manual trigger: send `/ask` in a group where the bot is present (admin-only by `ADMIN_USER_IDS`).
- Admin command `/groups` (works in private chat and groups) is available only for user IDs from `ADMIN_USER_IDS`.
- After successful admin commands in group chats, bot sends an extra notice that this command is admin-only.
