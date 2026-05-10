import unittest

from static_site_generator.html_node import HTMLNode


class TestHTMLNode(unittest.TestCase):
    def test_repr(self) -> None:
        pass

    def test_props_to_html(self) -> None:
        expected = 'href="https://www.google.com" target="_blank"'
        html_node = HTMLNode(
            props={"href": "https://www.google.com", "target": "_blank"},
        )
        result = html_node.props_to_html()
        assert result == expected

    def test_props_to_html_is_none(self) -> None:
        expected = ""
        html_node = HTMLNode()
        result = html_node.props_to_html()
        assert result == expected


if __name__ == "__main__":
    unittest.main()
