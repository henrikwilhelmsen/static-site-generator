# Copyright (C) 2026 Henrik Wilhelmsen.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at <https://mozilla.org/MPL/2.0/>.

import re

import pytest

from static_site_generator.models import BlockType, TextNode, TextType
from static_site_generator.parsing import (
    block_to_block_type,
    extract_markdown_images,
    extract_markdown_links,
    extract_title,
    markdown_to_blocks,
    markdown_to_html_node,
    split_nodes_delimiter,
    split_nodes_image,
    split_nodes_link,
    text_to_text_nodes,
)


@pytest.mark.parametrize(
    ("node", "delimiter", "text_type", "expected"),
    [
        (
            TextNode("This is text with a `code block` word", TextType.TEXT),
            "`",
            TextType.CODE,
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" word", TextType.TEXT),
            ],
        ),
        (
            TextNode("This is text with a **bold** word", TextType.TEXT),
            "**",
            TextType.BOLD,
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" word", TextType.TEXT),
            ],
        ),
        (
            TextNode(
                "This is text with multiple **bold** words **in it**",
                TextType.TEXT,
            ),
            "**",
            TextType.BOLD,
            [
                TextNode("This is text with multiple ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" words ", TextType.TEXT),
                TextNode("in it", TextType.BOLD),
            ],
        ),
        (
            TextNode(
                "This is text with multiple _italic_ words _in it_ as you _can see_.",
                TextType.TEXT,
            ),
            "_",
            TextType.ITALIC,
            [
                TextNode("This is text with multiple ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" words ", TextType.TEXT),
                TextNode("in it", TextType.ITALIC),
                TextNode(" as you ", TextType.TEXT),
                TextNode("can see", TextType.ITALIC),
                TextNode(".", TextType.TEXT),
            ],
        ),
    ],
)
def test_split_nodes_delimiter(
    node: TextNode,
    delimiter: str,
    text_type: TextType,
    expected: list[TextNode],
) -> None:
    result = split_nodes_delimiter([node], delimiter, text_type)
    assert result == expected


@pytest.mark.parametrize(
    ("nodes", "expected_exception", "match", "delimiter", "text_type"),
    [
        (
            [TextNode("This is text with a **missing bold delimiter", TextType.TEXT)],
            ValueError,
            "Invalid markdown syntax, text is missing a closing '**'",
            "**",
            TextType.BOLD,
        ),
        (
            [
                TextNode(
                    "This is a text node with **bold** delimiter",
                    TextType.TEXT,
                ),
                TextNode(
                    "This is text with a **missing** bold **delimiter",
                    TextType.TEXT,
                ),
            ],
            ValueError,
            "Invalid markdown syntax, text is missing a closing '**'",
            "**",
            TextType.BOLD,
        ),
        (
            [
                TextNode(
                    "This is a text node with an _italic_ delimiter",
                    TextType.TEXT,
                ),
                TextNode(
                    "This is **text** `with` a _missing_ italic _delimiter",
                    TextType.TEXT,
                ),
            ],
            ValueError,
            "Invalid markdown syntax, text is missing a closing '_'",
            "_",
            TextType.ITALIC,
        ),
    ],
)
def test_split_nodes_delimiter_raises(
    nodes: list[TextNode],
    expected_exception: type[BaseException],
    match: str,
    delimiter: str,
    text_type: TextType,
) -> None:
    # Escape the match string to avoid delimiters being interpreted as regex patterns
    with pytest.raises(expected_exception, match=re.escape(match)):
        split_nodes_delimiter(nodes, delimiter, text_type)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)",
            [("image", "https://i.imgur.com/zjjcJKZ.png")],
        ),
        (
            (
                "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and "
                "![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
            ),
            [
                ("rick roll", "https://i.imgur.com/aKaOqIh.gif"),
                ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg"),
            ],
        ),
    ],
)
def test_extract_markdown_images(text: str, expected: str) -> None:
    matches = extract_markdown_images(text)
    assert matches == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (
            (
                "This is text with a link [to boot dev](https://www.boot.dev) and "
                "[to youtube](https://www.youtube.com/@bootdotdev)"
            ),
            [
                ("to boot dev", "https://www.boot.dev"),
                ("to youtube", "https://www.youtube.com/@bootdotdev"),
            ],
        ),
    ],
)
def test_extract_markdown_links(text: str, expected: str) -> None:
    matches = extract_markdown_links(text)
    assert matches == expected


@pytest.mark.parametrize(
    ("old_nodes", "expected"),
    [
        (
            [
                TextNode(
                    "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) "
                    "and another ![second image](https://i.imgur.com/3elNhQu.png)",
                    TextType.TEXT,
                ),
            ],
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image",
                    TextType.IMAGE,
                    "https://i.imgur.com/3elNhQu.png",
                ),
            ],
        ),
        (
            [
                TextNode(
                    "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)",
                    TextType.TEXT,
                ),
            ],
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
            ],
        ),
        (
            [
                TextNode("This is text with no image", TextType.TEXT),
            ],
            [
                TextNode("This is text with no image", TextType.TEXT),
            ],
        ),
        (
            [
                TextNode(
                    "This is text with a [link](https://i.imgur.com/zjjcJKZ.png)",
                    TextType.TEXT,
                ),
            ],
            [
                TextNode(
                    "This is text with a [link](https://i.imgur.com/zjjcJKZ.png)",
                    TextType.TEXT,
                ),
            ],
        ),
        (
            [
                TextNode(
                    "![image only](https://i.imgur.com/zjjcJKZ.png)",
                    TextType.TEXT,
                ),
            ],
            [
                TextNode(
                    "image only",
                    TextType.IMAGE,
                    url="https://i.imgur.com/zjjcJKZ.png",
                ),
            ],
        ),
    ],
)
def test_split_images(old_nodes: list[TextNode], expected: list[TextNode]) -> None:
    new_nodes = split_nodes_image(old_nodes)
    assert new_nodes == expected


@pytest.mark.parametrize(
    ("old_nodes", "expected"),
    [
        (
            [
                TextNode(
                    "This is text with a [link](https://i.imgur.com/zjjcJKZ.png) "
                    "and another [second link](https://i.imgur.com/3elNhQu.png)",
                    TextType.TEXT,
                ),
            ],
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second link",
                    TextType.LINK,
                    "https://i.imgur.com/3elNhQu.png",
                ),
            ],
        ),
        (
            [
                TextNode(
                    "This is text with a [link](https://i.imgur.com/zjjcJKZ.png)",
                    TextType.TEXT,
                ),
            ],
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://i.imgur.com/zjjcJKZ.png"),
            ],
        ),
        (
            [
                TextNode("This is text with no link", TextType.TEXT),
            ],
            [
                TextNode("This is text with no link", TextType.TEXT),
            ],
        ),
        (
            [
                TextNode(
                    "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)",
                    TextType.TEXT,
                ),
            ],
            [
                TextNode(
                    "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)",
                    TextType.TEXT,
                ),
            ],
        ),
        (
            [
                TextNode(
                    "[link only](https://i.imgur.com/zjjcJKZ.png)",
                    TextType.TEXT,
                ),
            ],
            [
                TextNode(
                    "link only",
                    TextType.LINK,
                    url="https://i.imgur.com/zjjcJKZ.png",
                ),
            ],
        ),
    ],
)
def test_split_links(old_nodes: list[TextNode], expected: list[TextNode]) -> None:
    new_nodes = split_nodes_link(old_nodes)
    assert new_nodes == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (
            (
                "This is **text** with an _italic_ word and a `code block` and an "
                "![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
            ),
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode(
                    "obi wan image",
                    TextType.IMAGE,
                    "https://i.imgur.com/fJRm4Vk.jpeg",
                ),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
        ),
    ],
)
def test_text_to_text_nodes(text: str, expected: list[TextNode]) -> None:
    result = text_to_text_nodes(text)
    assert result == expected


def test_markdown_to_blocks() -> None:
    md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
    blocks = markdown_to_blocks(md)
    assert blocks == [
        "This is **bolded** paragraph",
        (
            "This is another paragraph with _italic_ text and `code` here\n"
            "This is the same paragraph on a new line"
        ),
        "- This is a list\n- with items",
    ]


@pytest.mark.parametrize(
    ("block", "expected_type"),
    [
        (
            """
### Some H3 Heading
            """.strip(),
            BlockType.HEADING,
        ),
        (
            """
```python
from foo import bar
bar.foo()
```
            """.strip(),
            BlockType.CODE,
        ),
        (
            """
> This is
> a
> quote block
            """.strip(),
            BlockType.QUOTE,
        ),
        (
            """
This is
just a
regular paragraph
            """.strip(),
            BlockType.PARAGRAPH,
        ),
        (
            """
- This is
- just an
- unordered
- list
            """.strip(),
            BlockType.UNORDERED_LIST,
        ),
        (
            """
1. This is
2. an
3. ordered
4. list
            """.strip(),
            BlockType.ORDERED_LIST,
        ),
    ],
)
def test_block_to_block_type(block: str, expected_type: BlockType) -> None:
    result = block_to_block_type(block)
    assert result == expected_type


@pytest.mark.parametrize(
    ("markdown", "expected_html"),
    [
        # Paragraph
        (
            """
This is **bold** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

""",
            (
                "<div><p>This is <b>bold</b> paragraph text in a p tag here</p>"
                "<p>This is "
                "another paragraph with <i>italic</i> text and <code>code</code> "
                "here</p></div>"
            ),
        ),
        # Code block
        (
            """
```
This is text that _should_ remain
the **same** even with inline stuff
```
""",
            (
                "<div><pre><code>\nThis is text that _should_ remain\nthe **same** "
                "even with inline stuff\n</code></pre></div>"
            ),
        ),
        # Header
        (
            """
### This is a header with some **bold** and _italic_ text
""",
            (
                "<div><h3>This is a header with some <b>bold</b> and <i>italic</i> "
                "text</h3></div>"
            ),
        ),
        # Block quote
        (
            """
> This is a block quote with some **bold** and _italic_ text.
> This is a block quote with some **bold** and _italic_ text
""",
            (
                "<div><blockquote>This is a block quote with some <b>bold</b> and "
                "<i>italic</i> text. "
                "This is a block quote with some <b>bold</b> and "
                "<i>italic</i> text</blockquote></div>"
            ),
        ),
        # Unordered list
        (
            """
- This is an unordered list entry with some **bold** and _italic_ text
- This is another unordered list entry with some `code` and _italic_ text
""",
            (
                "<div><ul><li>This is an unordered list entry with some <b>bold</b> "
                "and <i>italic</i> text</li>"
                "<li>This is another unordered list entry with some <code>code</code> "
                "and <i>italic</i> text</li></ul></div>"
            ),
        ),
        # Ordered list
        (
            """
1. This is an ordered list entry with some **bold** and _italic_ text
2. This is another ordered list entry with some `code` and _italic_ text
""",
            (
                "<div><ol><li>This is an ordered list entry with some <b>bold</b> and "
                "<i>italic</i> text</li>"
                "<li>This is another ordered list entry with some <code>code</code> "
                "and <i>italic</i> text</li></ol></div>"
            ),
        ),
    ],
)
def test_markdown_to_html_node(markdown: str, expected_html: str) -> None:
    node = markdown_to_html_node(markdown)
    result = node.to_html()
    assert result == expected_html


@pytest.mark.parametrize(
    ("markdown", "expected"),
    [
        (
            """
# Header **Title**
""",
            "Header **Title**",
        ),
        (
            """
# Another Header

in a multiline
document
""",
            "Another Header",
        ),
        (
            """
# Yet Another Header

in a multiline
document

## With

Several headers
""",
            "Yet Another Header",
        ),
    ],
)
def test_extract_title(markdown: str, expected: str) -> None:
    assert extract_title(markdown) == expected


@pytest.mark.parametrize(
    "markdown",
    [
        """
## Header two

body
""",
        """
No Header
at
all
""",
    ],
)
def test_extract_title_raises(markdown: str) -> None:
    with pytest.raises(ValueError, match="Markdown does not contain a title"):
        extract_title(markdown)
