import unittest

from static_site_generator.html_node import HTMLNode, LeafNode, ParentNode


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


class TestLeafNode(unittest.TestCase):
    def test_to_html_no_props_no_tags(self) -> None:
        expected = "This is some text"
        leaf_node = LeafNode(tag=None, value=expected)
        result = leaf_node.to_html()
        assert result == expected

    def test_leaf_to_html_p(self) -> None:
        result = LeafNode("p", "Hello, world!").to_html()
        assert result == "<p>Hello, world!</p>"

    def test_leaf_to_html_a_with_prop(self) -> None:
        result = LeafNode(
            "a",
            "Click me!",
            {"href": "https://www.google.com"},
        ).to_html()
        assert result == '<a href="https://www.google.com">Click me!</a>'

    def test_leaf_to_html_a_with_props(self) -> None:
        result = LeafNode(
            "a",
            "Click me!",
            {
                "href": "https://www.google.com",
                "target": "_blank",
            },
        ).to_html()
        assert (
            result == '<a href="https://www.google.com" target="_blank">Click me!</a>'
        )


class TestParentNode(unittest.TestCase):
    def test_leaf_to_html_p(self) -> None:
        node = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, "Normal text"),
                LeafNode("i", "italic text"),
                LeafNode(None, "Normal text"),
            ],
        )

        assert (
            node.to_html()
            == "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>"
        )

    def test_to_html_with_children(self) -> None:
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        assert parent_node.to_html() == "<div><span>child</span></div>"

    def test_to_html_with_grandchildren(self) -> None:
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        assert parent_node.to_html() == "<div><span><b>grandchild</b></span></div>"


if __name__ == "__main__":
    unittest.main()
