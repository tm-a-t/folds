import re

from telethon import helpers
from telethon.tl import types

from folds.markup.base import ParseError, TextDecoration

URL_ENTITY = object()
DELIMITERS = {
    '*': types.MessageEntityBold,
    '_': types.MessageEntityItalic,
    '__': types.MessageEntityUnderline,
    '~': types.MessageEntityStrike,
    '||': types.MessageEntitySpoiler,
    '`': types.MessageEntityCode,
    '```': types.MessageEntityPre,
    '[': URL_ENTITY,
    ']': URL_ENTITY,
}

QUOTE_PATTERN = re.compile(r'([_*\[\]()~`|\\])')
URL_RE = re.compile(r'\((.+?)\)')
URL_FORMAT = '[{0}]({1})'
LANG_RE = re.compile(r'[a-zA-Z0-9_-]{1,64}')


class MarkdownDecoration(TextDecoration):
    def apply_entity(self, entity: types.TypeMessageEntity, text: str) -> str:
        match entity:
            case types.MessageEntityBold():
                return f'*{text}*'
            case types.MessageEntityItalic():
                if text.startswith('_'):
                    return f'_\r{text}_'
                return f'_{text}_'
            case types.MessageEntityUnderline():
                if text.endswith('_'):
                    # awful hack
                    escape_cnt = 0
                    while len(text) >= escape_cnt + 2 and text[-escape_cnt - 2] == '\\':
                        escape_cnt += 1
                    if escape_cnt % 2 == 0:
                        # not escaped
                        return f'__{text}\r__'
                return f'__{text}__'
            case types.MessageEntityStrike():
                return f'~{text}~'
            case types.MessageEntitySpoiler():
                return f'||{text}||'
            case types.MessageEntityCode():
                return f'`{text}`'
            case types.MessageEntityPre(language=language):
                if language:
                    return f'```{language}\n{text}\n```'
                return f'```\n{text}\n```'
            case types.MessageEntityTextUrl(url=url):
                return URL_FORMAT.format(text, url)
            case types.MessageEntityEmail():
                return URL_FORMAT.format(text, f'mailto:{text}')
            case types.MessageEntityMentionName(user_id=user_id):
                return URL_FORMAT.format(text, f'tg://user?id={user_id}')
            case types.MessageEntityCustomEmoji(document_id=document_id):
                # TODO: this requires ![]() format in bot api?
                return URL_FORMAT.format(text, f'tg://emoji?id={document_id}')
            # TODO: support formatted date
        return text

    def quote(self, text: str, entity: types.TypeMessageEntity | None) -> str:
        if isinstance(entity, (types.MessageEntityPre, types.MessageEntityCode)):
            return text
        else:
            return QUOTE_PATTERN.sub(r'\\\1', text)

    def parse(self, text: str) -> tuple[str, list[types.TypeMessageEntity]]:
        if not text:
            return text, []

        # Build a regex to efficiently test all delimiters at once.
        # Note that the largest delimiter should go first, we don't
        # want ``` to be interpreted as a single back-tick in a code block.
        delim_re = re.compile('|'.join(f'({re.escape(k)})' for k in sorted(DELIMITERS, key=len, reverse=True)))

        # Work on byte level with the utf-16le encoding to get the offsets right.
        # The offset will just be half the index we're at.
        text = helpers.add_surrogate(text)

        # Cannot use a for loop because we need to skip some indices
        i = 0
        result = []
        delimiters_stack = []
        while i < len(text):
            if text[i] == '\r':
                # Remove \r, as in the TDLib/Bot API parser
                text = text[:i] + text[i + 1 :]
                continue

            last_opened_delim = delimiters_stack[-1] if delimiters_stack else (None, None)
            IN_CODE_BLOCK = last_opened_delim[0] in ('`', '```')
            if not IN_CODE_BLOCK and text[i] == '\\':
                # Remove the backslash and skip the next character
                text = text[:i] + text[i + 1 :]
                i += 1
                continue

            m = delim_re.match(text, pos=i)
            if not m:
                i += 1
                continue

            delim = next(filter(None, m.groups()))
            if IN_CODE_BLOCK and delim != last_opened_delim[0]:
                # ignore other delimiters inside a code block
                i += len(delim)
                continue

            if delim == ']':
                if last_opened_delim[0] != '[':
                    raise ParseError('Unexpected "]"')

                url_match = URL_RE.match(text, pos=i + 1)
                if not url_match:
                    raise ParseError('[] without ()')

                _, start = delimiters_stack.pop()
                result.append(
                    types.MessageEntityTextUrl(
                        offset=start,
                        length=i - start,
                        url=helpers.del_surrogate(url_match.group(1)),
                    )
                )
                # Remove the "](url)" part
                text = ''.join((text[:i], text[url_match.span()[1] :]))
                continue

            ent = DELIMITERS[delim]
            if last_opened_delim[0] != delim:
                # Open a new delimiter
                delimiters_stack.append((delim, i))

                # Remove the delimiter from the string
                # i should not be incremented
                text = ''.join((text[:i], text[i + len(delim) :]))
                continue

            # Close the last opened delimiter
            _, start = delimiters_stack.pop()

            if ent == types.MessageEntityPre:
                inner_text = text[start:i]
                # A language can be specified straight after the opening ``` delimiter
                lang = inner_text.split('\n', 1)[0]
                # We try to detect whether it's a language or the user just didn't insert
                # a line break after the opening delimiter
                if not LANG_RE.fullmatch(lang):
                    lang = ''
                # Remove the language and leading/trailing line breaks
                inner_text = inner_text[len(lang) :].removeprefix('\n').removesuffix('\n')

                # Remove the delimiter from the string
                text = ''.join((
                    text[:start],
                    inner_text,
                    text[i + len(delim) :],
                ))
                i = start + len(inner_text)

                result.append(ent(start, len(inner_text), lang))
            else:
                result.append(ent(start, i - start))
                # Remove the delimiter from the string
                text = ''.join((text[:i], text[i + len(delim) :]))
            continue

        text = helpers.strip_text(text, result)
        return self._post_parse(helpers.del_surrogate(text), result)


__all__ = ['MarkdownDecoration']
