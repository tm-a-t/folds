import re
from abc import ABC, abstractmethod
from collections.abc import Generator

from telethon.tl import types


class ParseError(Exception):
    pass


class TextDecoration(ABC):
    @abstractmethod
    def apply_entity(self, entity: types.TypeMessageEntity, text: str) -> str: ...

    @abstractmethod
    def quote(self, text: str, entity: types.TypeMessageEntity | None) -> str: ...

    @abstractmethod
    def parse(self, text: str) -> tuple[str, list[types.TypeMessageEntity]]:
        """
        Parses the given message with markup and returns its stripped representation
        plus a list of the MessageEntity's that were found.

        :param text: the message with markup to be parsed.
        :return: a tuple consisting of (clean message, [message entities]).
        """
        ...

    @staticmethod
    def _post_parse(text: str, entities: list[types.TypeMessageEntity]) -> tuple[str, list[types.TypeMessageEntity]]:
        for i in reversed(range(len(entities))):
            e = entities[i]
            if isinstance(e, types.MessageEntityTextUrl) and (m := re.match(r'^tg://emoji\?id=(\d+)$', e.url)):
                document_id = int(m.group(1))
                entities[i] = types.MessageEntityCustomEmoji(e.offset, e.length, document_id)
        return text, entities

    # Unparsing algorithm is based on aiogram's (https://github.com/aiogram/aiogram)
    def unparse(self, text: str, entities: list[types.TypeMessageEntity] | None = None) -> str:
        """
        Unparse message entities
        :param text: raw text
        :param entities: Array of MessageEntities
        :return:
        """
        return ''.join(
            self._unparse_entities(
                self._add_surrogates(text),
                sorted(entities, key=lambda item: (item.offset, -item.length)) if entities else [],
            )
        )

    def _unparse_entities(
        self,
        text: bytes,
        entities: list[types.TypeMessageEntity],
        offset: int | None = None,
        length: int | None = None,
        inside_entity: types.TypeMessageEntity | None = None,
    ) -> Generator[str, None, None]:
        if offset is None:
            offset = 0
        length = length or len(text)

        for index, entity in enumerate(entities):
            if entity.offset * 2 < offset:
                continue
            if entity.offset * 2 > offset:
                yield self.quote(
                    self._remove_surrogates(text[offset : entity.offset * 2]),
                    inside_entity,
                )
            start = entity.offset * 2
            offset = entity.offset * 2 + entity.length * 2

            sub_entities = list(filter(lambda e: e.offset * 2 < (offset or 0), entities[index + 1 :]))
            yield self.apply_entity(
                entity,
                ''.join(
                    self._unparse_entities(
                        text,
                        sub_entities,
                        offset=start,
                        length=offset,
                        inside_entity=entity,
                    )
                ),
            )

        if offset < length:
            yield self.quote(self._remove_surrogates(text[offset:length]), inside_entity)

    @staticmethod
    def _add_surrogates(text: str) -> bytes:
        return text.encode('utf-16-le')

    @staticmethod
    def _remove_surrogates(text: bytes) -> str:
        return text.decode('utf-16-le')


__all__ = ['TextDecoration', 'ParseError']
