from folds.markup import markdown
from telethon.tl.types import (
    MessageEntityBold,
    MessageEntityItalic,
    MessageEntityTextUrl,
    MessageEntityPre,
    MessageEntityCode,
    MessageEntityUnderline,
    MessageEntityStrike,
    MessageEntitySpoiler,
    MessageEntityUrl,
)


def test_entity_edges():
    """
    Test that entities at the edges (start and end) don't crash.
    """
    text = 'Hello, world'
    entities = [MessageEntityBold(0, 5), MessageEntityBold(7, 5)]
    result = markdown.unparse(text, entities)
    assert result == '*Hello*, *world*'


def test_malformed_entities():
    """
    Test that malformed entity offsets from bad clients
    don't crash and produce the expected results.
    """
    text = '🏆Telegram Official Android Challenge is over🏆.'
    entities = [MessageEntityTextUrl(offset=2, length=43, url='https://example.com')]
    result = markdown.unparse(text, entities)
    assert (
        result
        == "🏆[Telegram Official Android Challenge is over](https://example.com)🏆."
    )


def test_trailing_malformed_entities():
    """
    Similar to `test_malformed_entities`, but for the edge
    case where the malformed entity offset is right at the end
    (note the lack of a trailing dot in the text string).
    """
    text = '🏆Telegram Official Android Challenge is over🏆'
    entities = [MessageEntityTextUrl(offset=2, length=43, url='https://example.com')]
    result = markdown.unparse(text, entities)
    assert (
        result == "🏆[Telegram Official Android Challenge is over](https://example.com)🏆"
    )


def test_entities_together():
    """
    Test that an entity followed immediately by a different one behaves well.
    """
    original = '*⚙️*_Settings_'
    stripped = '⚙️Settings'

    text, entities = markdown.parse(original)
    assert text == stripped
    assert entities == [MessageEntityBold(0, 2), MessageEntityItalic(2, 8)]

    text = markdown.unparse(text, entities)
    assert text == original


def test_offset_at_emoji():
    """
    Tests that an entity starting at a emoji preserves the emoji.
    """
    text = 'Hi\n👉 See example'
    entities = [
        MessageEntityBold(0, 2),
        MessageEntityItalic(3, 2),
        MessageEntityBold(10, 7),
    ]
    parsed = '*Hi*\n_👉_ See *example*'

    assert markdown.parse(parsed) == (text, entities)
    assert markdown.unparse(text, entities) == parsed


def test_escaped_delimiters():
    """
    Tests that escaped delimiters are ignored.
    """
    original = r'__\_\_\___ _\__ ~\_~ ||\~|| ||\[|| ~\`~ ~\~~ [\*\]\[\(](https://vanutp.dev)'
    stripped = '___ _ _ ~ [ ` ~ *][('
    entities = [
        MessageEntityUnderline(offset=0, length=3),
        MessageEntityItalic(offset=4, length=1),
        MessageEntityStrike(offset=6, length=1),
        MessageEntitySpoiler(offset=8, length=1),
        MessageEntitySpoiler(offset=10, length=1),
        MessageEntityStrike(offset=12, length=1),
        MessageEntityStrike(offset=14, length=1),
        MessageEntityTextUrl(offset=16, length=4, url='https://vanutp.dev'),
    ]

    assert markdown.parse(original) == (stripped, entities)
    assert markdown.unparse(stripped, entities) == original


def test_pre_lang():
    """
    Tests that language in pre block is parsed correctly.
    """
    original = '```python\nsome code\n``` ```some code``` ```some code\n```'
    expected = '```python\nsome code\n``` ```\nsome code\n``` ```\nsome code\n```'
    stripped = 'some code some code some code'
    entities = [
        MessageEntityPre(0, 9, 'python'),
        MessageEntityPre(10, 9, ''),
        MessageEntityPre(20, 9, ''),
    ]

    assert markdown.parse(original) == (stripped, entities)
    assert markdown.unparse(stripped, entities) == expected


def test_entities_inside_pre_block():
    """
    Tests that other entities and escapes inside pre block are ignored.
    """
    original = '```\n*bold* _italic_ __underline__ ~strikethrough~ ||spoiler|| `code` [url](https://vanutp.dev)\\`\n```'
    stripped = original[4:-4]
    entities = [MessageEntityPre(0, len(stripped), '')]

    assert markdown.parse(original) == (stripped, entities)
    assert markdown.unparse(stripped, entities) == original


def test_entities_inside_url():
    """
    Tests that entities inside url are parsed.
    """
    original = '[*bold* _italic_ __underline__ ~strikethrough~ ||spoiler|| `code`](https://vanutp.dev/\\) no entity'
    stripped = 'bold italic underline strikethrough spoiler code no entity'
    entities = [
        MessageEntityBold(offset=0, length=4),
        MessageEntityItalic(offset=5, length=6),
        MessageEntityUnderline(offset=12, length=9),
        MessageEntityStrike(offset=22, length=13),
        MessageEntitySpoiler(offset=36, length=7),
        MessageEntityCode(offset=44, length=4),
        MessageEntityTextUrl(offset=0, length=48, url='https://vanutp.dev/\\'),
    ]

    assert markdown.parse(original) == (stripped, entities)
    assert markdown.unparse(stripped, entities) == original


def test_markdownv2_example():
    """
    Tests that the example from telegram docs is parsed correctly.
    """
    original = r'''*bold \*text*
_italic \*text_
__underline__
~strikethrough~
||spoiler||
*bold _italic bold ~italic bold strikethrough ||italic bold strikethrough spoiler||~ __underline italic bold___ bold*
[inline URL](http://www.example.com/)
[inline mention of a user](tg://user?id=123456789)
`inline fixed-width code`
```
pre-formatted fixed-width code block
```
```python
pre-formatted fixed-width code block written in the Python programming language
```'''
    stripped = '''bold *text
italic *text
underline
strikethrough
spoiler
bold italic bold italic bold strikethrough italic bold strikethrough spoiler underline italic bold bold
inline URL
inline mention of a user
inline fixed-width code
pre-formatted fixed-width code block
pre-formatted fixed-width code block written in the Python programming language'''
    entities = [
        MessageEntityBold(offset=0, length=10),
        MessageEntityItalic(offset=11, length=12),
        MessageEntityUnderline(offset=24, length=9),
        MessageEntityStrike(offset=34, length=13),
        MessageEntitySpoiler(offset=48, length=7),
        MessageEntitySpoiler(offset=99, length=33),
        MessageEntityStrike(offset=73, length=59),
        MessageEntityUnderline(offset=133, length=21),
        MessageEntityItalic(offset=61, length=93),
        MessageEntityBold(offset=56, length=103),
        MessageEntityTextUrl(offset=160, length=10, url='http://www.example.com/'),
        MessageEntityTextUrl(offset=171, length=24, url='tg://user?id=123456789'),
        MessageEntityCode(offset=196, length=23),
        MessageEntityPre(offset=220, length=36, language=''),
        MessageEntityPre(offset=257, length=79, language='python'),
    ]

    assert markdown.parse(original) == (stripped, entities)
    assert markdown.unparse(stripped, entities) == original


def test_italic_underline():
    """
    Tests that italic and underline can be used together.
    """
    original = '___italic underline_\r__ no entity'
    stripped = 'italic underline no entity'
    entities = [
        MessageEntityItalic(offset=0, length=16),
        MessageEntityUnderline(offset=0, length=16),
    ]
    expected = [
        original,
        '_\r__italic underline___ no entity',
    ]

    assert markdown.parse(original) == (stripped, entities)
    assert markdown.unparse(stripped, entities) in expected
