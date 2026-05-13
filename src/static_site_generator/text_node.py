import json
from enum import Enum

from static_site_generator.html_node import HTMLNode, LeafNode


class TextType(Enum):
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"


class TextNode:
    def __init__(self, text: str, text_type: TextType, url: str | None = None) -> None:
        self.text: str = text
        self.text_type: TextType = text_type
        self.url: str | None = url

    def __eq__(self, other: object) -> bool:
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False

    def __hash__(self) -> int:
        return hash((self.text, self.text_type, self.url))

    def __repr__(self) -> str:
        return json.dumps(
            {
                "class": "TextNode",
                "text": self.text,
                "text_type": self.text_type.value,
                "url": self.url,
            },
            indent=2,
        )


def text_node_to_html_node(text_node: TextNode) -> HTMLNode:
    match text_node.text_type:
        case TextType.TEXT:
            return LeafNode(tag=None, value=text_node.text)
        case TextType.BOLD:
            return LeafNode(tag="b", value=text_node.text)
        case TextType.ITALIC:
            return LeafNode(tag="i", value=text_node.text)
        case TextType.CODE:
            return LeafNode(tag="code", value=text_node.text)
        case TextType.LINK:
            if text_node.url is None:
                msg = "Link text node is missing a URL"
                raise ValueError(msg)

            return LeafNode(
                tag="a",
                value=text_node.text,
                props={"href": text_node.url},
            )
        case TextType.IMAGE:
            if text_node.url is None:
                msg = "Image text node is missing a URL"
                raise ValueError(msg)

            return LeafNode(
                tag="img",
                value=text_node.text,
                props={"src": text_node.url},
            )
        case _:
            msg = f"Invalid text type for node '{text_node}'"
            raise ValueError
