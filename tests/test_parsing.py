import unittest

import pytest

from static_site_generator.parsing import split_nodes_delimiter
from static_site_generator.text_node import TextNode, TextType


class TestTextNode(unittest.TestCase):
    def test_code(self) -> None:
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        assert new_nodes == [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" word", TextType.TEXT),
        ]

    def test_bold(self) -> None:
        node = TextNode("This is text with a **bold** word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        assert new_nodes == [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" word", TextType.TEXT),
        ]

    def test_bold_multiple(self) -> None:
        node = TextNode(
            "This is text with multiple **bold** words **in it**",
            TextType.TEXT,
        )
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        assert new_nodes == [
            TextNode("This is text with multiple ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" words ", TextType.TEXT),
            TextNode("in it", TextType.BOLD),
        ]

    def test_italic_multiple(self) -> None:
        node = TextNode(
            "This is text with multiple _italic_ words _in it_ as you _can see_.",
            TextType.TEXT,
        )
        new_nodes = split_nodes_delimiter([node], "_", TextType.ITALIC)
        assert new_nodes == [
            TextNode("This is text with multiple ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" words ", TextType.TEXT),
            TextNode("in it", TextType.ITALIC),
            TextNode(" as you ", TextType.TEXT),
            TextNode("can see", TextType.ITALIC),
            TextNode(".", TextType.TEXT),
        ]

    def test_no_delimiter_raises(self) -> None:
        node = TextNode("This is text with a no delimiter", TextType.TEXT)
        with pytest.raises(ValueError, match="No delimiter"):
            split_nodes_delimiter([node], "**", TextType.BOLD)

    def test_missing_closing_delimiter_raises(self) -> None:
        node = TextNode("This is text with a **missing bold delimiter", TextType.TEXT)
        msg = "Invalid markdown syntax, text is missing a closing"
        with pytest.raises(ValueError, match=msg):
            split_nodes_delimiter([node], "**", TextType.BOLD)

    def test_missing_closing_delimiter_multiple_raises(self) -> None:
        node = TextNode(
            "This is text with a **missing** bold **delimiter",
            TextType.TEXT,
        )
        msg = "Invalid markdown syntax, text is missing a closing"
        with pytest.raises(ValueError, match=msg):
            split_nodes_delimiter([node], "**", TextType.BOLD)
