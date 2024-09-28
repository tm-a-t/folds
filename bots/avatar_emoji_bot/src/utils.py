TITLE_SUFFIX = ' Avatars'
TITLE_LOWER_SUFFIX = ' avatars'
LINK_PREFIX = 'avatars_1'


def get_set_title(chat_title: str):
    chat_title = chat_title.split(': ')[0]

    chat_title_words = chat_title.split(' ')
    for i, word in enumerate(chat_title_words):
        if not any(c.isalpha() or c.isdigit() or c == '&' for c in word) and i > 0:
            chat_title_words = chat_title_words[:i]
            break
    chat_title = ' '.join(chat_title_words).strip()

    letters = [c for c in chat_title if c.isalpha()]
    if letters and letters[0].islower():
        return chat_title + TITLE_LOWER_SUFFIX
    else:
        return chat_title + TITLE_SUFFIX


def get_set_link(chat_id: int, username: str):
    return f'{LINK_PREFIX}_{chat_id}_by_{username}'


def get_full_set_link(chat_id: int, username: str):
    return 'https://t.me/addemoji/' + get_set_link(chat_id, username)


def get_chat_set_link(event: events.ChatAction.Event | Message) -> str:
    link = get_full_set_link(event.chat.id, event.client.me.username)
    title = get_set_title(event.chat.title)
    return f'<a href="{link}">{title}</a>'
