from static_site_generator.html_node import HTMLNode
from static_site_generator.text_node import TextNode, TextType


def main() -> None:
    text_node = TextNode(
        "This is some anchor text",
        TextType.LINK,
        "https://www.boot.dev",
    )
    html_node = HTMLNode(
        children=[
            HTMLNode(tag="foo", value="bar"),
            HTMLNode(tag="foo", value="bar"),
            HTMLNode(tag="foo", value="bar"),
            HTMLNode(tag="foo", value="bar"),
            HTMLNode(tag="foo", value="bar"),
        ],
    )
    html_node2 = HTMLNode()
    print(text_node)
    print(html_node)
    print(html_node2)
