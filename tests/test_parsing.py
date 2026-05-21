import re

import pytest

from static_site_generator.parsing import (
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_delimiter,
    split_nodes_image,
    split_nodes_link,
)
from static_site_generator.text_node import TextNode, TextType


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
            [TextNode("This is text with no delimiter", TextType.TEXT)],
            ValueError,
            "No delimiter",
            "**",
            TextType.BOLD,
        ),
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
            "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and "
            "![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)",
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
            "This is text with a link [to boot dev](https://www.boot.dev) and "
            "[to youtube](https://www.youtube.com/@bootdotdev)",
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
