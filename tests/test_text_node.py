import unittest

from static_site_generator.text_node import TextNode, TextType


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


if __name__ == "__main__":
    unittest.main()
