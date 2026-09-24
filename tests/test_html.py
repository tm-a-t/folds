from folds.markup import html
from telethon.tl.types import (
    MessageEntityBold,
    MessageEntityItalic,
    MessageEntityTextUrl,
    MessageEntityUnderline,
    MessageEntityStrike,
    MessageEntitySpoiler,
    MessageEntityPre,
    MessageEntityCode,
)


def test_entity_edges():
    """
    Test that entities at the edges (start and end) don't crash.
    """
    text = 'Hello, world'
    entities = [MessageEntityBold(0, 5), MessageEntityBold(7, 5)]
    result = html.unparse(text, entities)
    assert result == '<b>Hello</b>, <b>world</b>'


def test_malformed_entities():
    """
    Test that malformed entity offsets from bad clients
    don't crash and produce the expected results.
    """
    text = '🏆Telegram Official Android Challenge is over🏆.'
    entities = [MessageEntityTextUrl(offset=2, length=43, url='https://example.com')]
    result = html.unparse(text, entities)
    assert (
        result
        == '🏆<a href="https://example.com">Telegram Official Android Challenge is over</a>🏆.'
    )


def test_trailing_malformed_entities():
    """
    Similar to `test_malformed_entities`, but for the edge
    case where the malformed entity offset is right at the end
    (note the lack of a trailing dot in the text string).
    """
    text = '🏆Telegram Official Android Challenge is over🏆'
    entities = [MessageEntityTextUrl(offset=2, length=43, url='https://example.com')]
    result = html.unparse(text, entities)
    assert (
        result
        == '🏆<a href="https://example.com">Telegram Official Android Challenge is over</a>🏆'
    )


def test_entities_together():
    """
    Test that an entity followed immediately by a different one behaves well.
    """
    original = '<b>⚙️</b><i>Settings</i>'
    stripped = '⚙️Settings'

    text, entities = html.parse(original)
    assert text == stripped
    assert entities == [MessageEntityBold(0, 2), MessageEntityItalic(2, 8)]

    text = html.unparse(text, entities)
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
    parsed = '<b>Hi</b>\n<i>👉</i> See <b>example</b>'

    assert html.parse(parsed) == (text, entities)
    assert html.unparse(text, entities) == parsed


def test_bot_api_example():
    """
    Tests that the example from telegram docs is parsed correctly.
    """
    original = '''<b>bold</b>, <strong>bold</strong>
<i>italic</i>, <em>italic</em>
<u>underline</u>, <ins>underline</ins>
<s>strikethrough</s>, <strike>strikethrough</strike>, <del>strikethrough</del>
<span class="tg-spoiler">spoiler</span>, <tg-spoiler>spoiler</tg-spoiler>
<b>bold <i>italic bold <s>italic bold strikethrough <span class="tg-spoiler">italic bold strikethrough spoiler</span></s> <u>underline italic bold</u></i> bold</b>
<a href="http://www.example.com/">inline URL</a>
<a href="tg://user?id=123456789">inline mention of a user</a>
<code>inline fixed-width code</code>
<pre>pre-formatted fixed-width code block</pre>
<pre><code class="language-python">pre-formatted fixed-width code block written in the Python programming language</code></pre>'''
    stripped = '''bold, bold
italic, italic
underline, underline
strikethrough, strikethrough, strikethrough
spoiler, spoiler
bold italic bold italic bold strikethrough italic bold strikethrough spoiler underline italic bold bold
inline URL
inline mention of a user
inline fixed-width code
pre-formatted fixed-width code block
pre-formatted fixed-width code block written in the Python programming language'''
    entities = [
        MessageEntityBold(offset=0, length=4),
        MessageEntityBold(offset=6, length=4),
        MessageEntityItalic(offset=11, length=6),
        MessageEntityItalic(offset=19, length=6),
        MessageEntityUnderline(offset=26, length=9),
        MessageEntityUnderline(offset=37, length=9),
        MessageEntityStrike(offset=47, length=13),
        MessageEntityStrike(offset=62, length=13),
        MessageEntityStrike(offset=77, length=13),
        MessageEntitySpoiler(offset=91, length=7),
        MessageEntitySpoiler(offset=100, length=7),
        MessageEntitySpoiler(offset=151, length=33),
        MessageEntityStrike(offset=125, length=59),
        MessageEntityUnderline(offset=185, length=21),
        MessageEntityItalic(offset=113, length=93),
        MessageEntityBold(offset=108, length=103),
        MessageEntityTextUrl(offset=212, length=10, url='http://www.example.com/'),
        MessageEntityTextUrl(offset=223, length=24, url='tg://user?id=123456789'),
        MessageEntityCode(offset=248, length=23),
        MessageEntityPre(offset=272, length=36, language=''),
        MessageEntityPre(offset=309, length=79, language='python'),
    ]
    expected = '''<b>bold</b>, <b>bold</b>
<i>italic</i>, <i>italic</i>
<u>underline</u>, <u>underline</u>
<s>strikethrough</s>, <s>strikethrough</s>, <s>strikethrough</s>
<span class="tg-spoiler">spoiler</span>, <span class="tg-spoiler">spoiler</span>
<b>bold <i>italic bold <s>italic bold strikethrough <span class="tg-spoiler">italic bold strikethrough spoiler</span></s> <u>underline italic bold</u></i> bold</b>
<a href="http://www.example.com/">inline URL</a>
<a href="tg://user?id=123456789">inline mention of a user</a>
<code>inline fixed-width code</code>
<pre>pre-formatted fixed-width code block</pre>
<pre><code class="language-python">pre-formatted fixed-width code block written in the Python programming language</code></pre>'''

    assert html.parse(original) == (stripped, entities)
    assert html.unparse(stripped, entities) == expected


def test_parser_close() -> None:
    assert html.parse('https://vanutp.dev?a=b&c=d') == ('https://vanutp.dev?a=b&c=d', [])


def test_url_emoji() -> None:
    original = '<a href="https://vanutp.dev/🦊">🦊</a>'
    stripped = '🦊'
    entities = [MessageEntityTextUrl(0, 2, 'https://vanutp.dev/🦊')]

    assert html.parse(original) == (stripped, entities)
    assert html.unparse(stripped, entities) == original

