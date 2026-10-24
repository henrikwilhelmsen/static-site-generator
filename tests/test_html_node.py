# Copyright (C) 2026 Henrik Wilhelmsen.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at <https://mozilla.org/MPL/2.0/>.

import unittest

from static_site_generator.models import HTMLLeafNode, HTMLNode, HTMLParentNode


class TestHTMLNode(unittest.TestCase):
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
        leaf_node = HTMLLeafNode(tag=None, value=expected)
        result = leaf_node.to_html()
        assert result == expected

    def test_leaf_to_html_p(self) -> None:
        result = HTMLLeafNode("p", "Hello, world!").to_html()
        assert result == "<p>Hello, world!</p>"

    def test_leaf_to_html_a_with_prop(self) -> None:
        result = HTMLLeafNode(
            "a",
            "Click me!",
            {"href": "https://www.google.com"},
        ).to_html()
        assert result == '<a href="https://www.google.com">Click me!</a>'

    def test_leaf_to_html_a_with_props(self) -> None:
        result = HTMLLeafNode(
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
        node = HTMLParentNode(
            "p",
            [
                HTMLLeafNode("b", "Bold text"),
                HTMLLeafNode(None, "Normal text"),
                HTMLLeafNode("i", "italic text"),
                HTMLLeafNode(None, "Normal text"),
            ],
        )

        assert (
            node.to_html()
            == "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>"
        )

    def test_to_html_with_children(self) -> None:
        child_node = HTMLLeafNode("span", "child")
        parent_node = HTMLParentNode("div", [child_node])
        assert parent_node.to_html() == "<div><span>child</span></div>"

    def test_to_html_with_grandchildren(self) -> None:
        grandchild_node = HTMLLeafNode("b", "grandchild")
        child_node = HTMLParentNode("span", [grandchild_node])
        parent_node = HTMLParentNode("div", [child_node])
        assert parent_node.to_html() == "<div><span><b>grandchild</b></span></div>"


if __name__ == "__main__":
    unittest.main()
