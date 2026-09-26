import html as _html
from collections import deque
from html.parser import HTMLParser

from telethon import helpers
from telethon.tl import types

from folds.markup.base import TextDecoration


class HTMLToTelegramParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = ''
        self.entities = []
        self._building_entities = {}
        self._open_tags = deque()
        self._open_tags_meta = deque()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        self._open_tags.appendleft(tag)
        self._open_tags_meta.appendleft(None)

        attrs_d = dict(attrs)
        EntityType = None
        args = {}
        if tag == 'strong' or tag == 'b':
            EntityType = types.MessageEntityBold
        elif tag in ['em', 'i']:
            EntityType = types.MessageEntityItalic
        elif tag in ['u', 'ins']:
            EntityType = types.MessageEntityUnderline
        elif tag in ['del', 's', 'strike']:
            EntityType = types.MessageEntityStrike
        elif tag == 'blockquote':
            EntityType = types.MessageEntityBlockquote
            if 'expandable' in attrs_d:
                args['collapsed'] = True
        elif tag == 'code':
            try:
                # If we're in the middle of a <pre> tag, this <code> tag is
                # probably intended for syntax highlighting.
                #
                # Syntax highlighting is set with
                #     <code class='language-...'>codeblock</code>
                # inside <pre> tags
                pre = self._building_entities['pre']
                try:
                    pre.language = attrs_d['class'][len('language-'):]
                except KeyError:
                    pass
            except KeyError:
                EntityType = types.MessageEntityCode
        elif tag == 'pre':
            EntityType = types.MessageEntityPre
            args['language'] = ''
        elif tag == 'tg-emoji' or tag == 'emoji':
            EntityType = types.MessageEntityCustomEmoji
            for attr in ('document', 'document_id', 'document-id', 'emoji', 'emoji_id', 'emoji-id'):
                if attr in attrs_d:
                    args['document_id'] = int(attrs_d[attr])
                    break
        elif tag == 'span' and attrs_d['class'] == 'tg-spoiler' or tag == 'tg-spoiler':
            EntityType = types.MessageEntitySpoiler
        elif tag == 'a':
            try:
                url = attrs_d['href']
            except KeyError:
                return
            if url.startswith('mailto:'):
                url = url[len('mailto:') :]
                EntityType = types.MessageEntityEmail
            else:
                if self.get_starttag_text() == url:
                    EntityType = types.MessageEntityUrl
                else:
                    EntityType = types.MessageEntityTextUrl
                    args['url'] = helpers.del_surrogate(url)
                    url = None
            self._open_tags_meta.popleft()
            self._open_tags_meta.appendleft(url)

        if EntityType and tag not in self._building_entities:
            self._building_entities[tag] = EntityType(
                offset=len(self.text),
                # The length will be determined when closing the tag.
                length=0,
                **args,
            )

    def handle_data(self, data: str):
        previous_tag = self._open_tags[0] if len(self._open_tags) > 0 else ''
        if previous_tag == 'a':
            url = self._open_tags_meta[0]
            if url:
                data = url

        for entity in self._building_entities.values():
            entity.length += len(data)

        self.text += data

    def handle_endtag(self, tag: str):
        try:
            self._open_tags.popleft()
            self._open_tags_meta.popleft()
        except IndexError:
            pass
        entity = self._building_entities.pop(tag, None)
        if entity:
            self.entities.append(entity)


class HtmlDecoration(TextDecoration):
    def apply_entity(self, entity: types.TypeMessageEntity, text: str) -> str:
        match entity:
            case types.MessageEntityBold():
                return f'<b>{text}</b>'
            case types.MessageEntityItalic():
                return f'<i>{text}</i>'
            case types.MessageEntityUnderline():
                return f'<u>{text}</u>'
            case types.MessageEntityStrike():
                return f'<s>{text}</s>'
            case types.MessageEntitySpoiler():
                return f'<span class="tg-spoiler">{text}</span>'
            case types.MessageEntityCode():
                return f'<code>{text}</code>'
            case types.MessageEntityPre(language=language):
                if language:
                    return f'<pre><code class="language-{language}">{text}</code></pre>'
                return f'<pre>{text}</pre>'
            case types.MessageEntityTextUrl(url=url):
                return f'<a href="{url}">{text}</a>'
            case types.MessageEntityEmail:
                return f'<a href="mailto:{text}">{text}</a>'
            case types.MessageEntityMentionName(user_id=user_id):
                return f'<a href="tg://user?id={user_id}">{text}</a>'
            case types.MessageEntityCustomEmoji(document_id=document_id):
                return f'<tg-emoji emoji-id="{document_id}">{text}</tg-emoji>'
            case types.MessageEntityBlockquote(collapsed=collapsed):
                if collapsed:
                    return f'<blockquote expandable>{text}</blockquote>'
                return f'<blockquote>{text}</blockquote>'
            # TODO: support formatted date
        return text

    def quote(self, text: str, entity: types.TypeMessageEntity | None) -> str:
        return _html.escape(text, quote=False)

    def parse(self, text: str) -> tuple[str, list[types.TypeMessageEntity]]:
        if not text:
            return text, []

        parser = HTMLToTelegramParser()
        parser.feed(helpers.add_surrogate(text))
        parser.close()
        text = helpers.strip_text(parser.text, parser.entities)
        return self._post_parse(helpers.del_surrogate(text), parser.entities)


__all__ = ['HtmlDecoration']
