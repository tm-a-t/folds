import hashlib
from io import BytesIO
from random import randint

from PIL import Image
from telethon.errors import BadRequestError, StickersetInvalidError
from telethon.functions import stickers, messages
from telethon.tl import types as tl_types
from telethon.tl.functions.messages import UploadMediaRequest
from telethon.types import Chat, Channel
from telethon.utils import get_input_document

from avatar_emoji_bot.utils import get_set_title, get_set_link, Emoji
from folds.context import client

mask_image = Image.open('mask.png').convert('L')
fallback_emoji = '🟣'


async def update_or_create_set(chat: Chat | Channel, user_id: int) -> bool:
    emojis = await _create_emojis_from_profiles(chat)

    try:
        emoji_set: tl_types.messages.StickerSet = await _get_set(chat)
    except StickersetInvalidError:
        await _create_set(chat, user_id, emojis)
        return True

    await _update_set(chat, emoji_set, emojis)
    return False


async def _get_set(chat: Chat | Channel) -> tl_types.messages.StickerSet:
    link = get_set_link(chat.id, client.me.username)
    get_set_request = messages.GetStickerSetRequest(tl_types.InputStickerSetShortName(link), hash=randint(1, 10 ** 9))
    return await client(get_set_request)


async def _create_set(chat: Chat | Channel, user_id: int, emojis: list[Emoji]):
    title = get_set_title(chat.title)
    link = get_set_link(chat.id, client.me.username)

    request = stickers.CreateStickerSetRequest(user_id, title, link, emojis, emojis=True)
    await client(request)


async def _update_set(chat: Chat | Channel, emoji_set: tl_types.messages.StickerSet, emojis: list[Emoji]):
    title = get_set_title(chat.title)
    link = get_set_link(chat.id, client.me.username)
    input_emoji_set = tl_types.InputStickerSetShortName(link)

    if emoji_set.set.title != title:
        update_title_request = stickers.RenameStickerSetRequest(input_emoji_set, title)
        await client(update_title_request)

    for emoji in emojis:
        add_request = stickers.AddStickerToSetRequest(input_emoji_set, emoji)
        await client(add_request)

    for document in emoji_set.documents:
        remove_request = stickers.RemoveStickerFromSetRequest(get_input_document(document))
        try:
            await client(remove_request)
        except BadRequestError:
            pass


async def _create_emojis_from_profiles(chat: Chat | Channel) -> list[Emoji]:
    items = []

    if chat.photo:
        photo: bytes = await client.download_profile_photo(chat, bytes)
        items.append(await _create_emoji(photo))

    async for user in client.iter_participants(chat):
        if user.is_self:
            continue
        if user.photo is None or isinstance(user.photo, tl_types.UserProfilePhotoEmpty):
            continue

        photo: bytes = await client.download_profile_photo(user, bytes)
        items.append(await _create_emoji(photo, keywords=user.username or None))

        if len(items) == 120:
            # reached max number of emoji
            break

    return items


async def _create_emoji(original_photo: bytes, *, keywords: str = None) -> Emoji:
    new_photo = _create_image(original_photo)

    file = await client.upload_file(new_photo)
    mime = 'image/webp'
    uploaded_document = tl_types.InputMediaUploadedDocument(file, mime, [])
    media = await client(UploadMediaRequest(tl_types.InputPeerSelf(), uploaded_document))
    input_document = get_input_document(media)

    return Emoji(input_document, fallback_emoji, new_photo, keywords=keywords)


def _create_image(original_photo: bytes) -> bytes:
    new_photo_bytes_io = BytesIO()
    image = Image.open(BytesIO(original_photo))
    image_resized = image.resize((90, 90))
    image_resized.putalpha(mask_image)
    container_image = Image.new('RGBA', (100, 100), (255, 0, 0, 0))
    container_image.paste(image_resized, (5, 5))
    container_image.save(new_photo_bytes_io, format='webp')
    return new_photo_bytes_io.getvalue()


async def _get_emoji_set_hash_set(emoji_set: tl_types.messages.StickerSet):
    hash_set = set()
    for document in emoji_set.documents:
        emoji_bytes = await client.download_file(document, bytes)
        emoji_hash = hashlib.sha256(emoji_bytes).hexdigest()
        hash_set.add(emoji_hash)
    return hash_set
