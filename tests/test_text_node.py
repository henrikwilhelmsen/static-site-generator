import unittest

import pytest

from static_site_generator.text_node import TextNode, TextType, text_node_to_html_node


class TestTextNode(unittest.TestCase):
    def test_equal(self) -> None:
        node1 = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        assert node1 == node2

    def test_not_equal(self) -> None:
        node1 = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is another text node", TextType.ITALIC)
        assert node1 != node2

    def test_not_equal_url_none_str(self) -> None:
        node = TextNode("This is a text node", TextType.BOLD, None)
        node2 = TextNode(
            "This is another text node",
            TextType.LINK,
            "https://www.example.com",
        )
        assert node != node2

    def test_not_equal_url_str(self) -> None:
        node = TextNode("This is a text node", TextType.IMAGE, "some-image-url")
        node2 = TextNode(
            "This is another text node",
            TextType.LINK,
            "https://www.example.com",
        )
        assert node != node2


class TestTextNodeToHTMLNode(unittest.TestCase):
    def test_plain(self) -> None:
        text_node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(text_node)
        assert html_node.tag is None
        assert html_node.value == "This is a text node"

    def test_bold(self) -> None:
        text_node = TextNode("This is a bold text node", TextType.BOLD)
        html_node = text_node_to_html_node(text_node)
        assert html_node.tag == "b"

    def test_link(self) -> None:
        text_node = TextNode(
            "This is a link node",
            TextType.LINK,
            url="https://www.example.com",
        )
        html_node = text_node_to_html_node(text_node)
        assert html_node.tag == "a"
        assert html_node.props == {"href": "https://www.example.com"}

    def test_link_raises(self) -> None:
        text_node = TextNode(
            "This is a link node with not url",
            TextType.LINK,
        )
        with pytest.raises(ValueError, match="Link text node is missing a URL"):
            text_node_to_html_node(text_node)


if __name__ == "__main__":
    unittest.main()
