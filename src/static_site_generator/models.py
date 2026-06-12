import json
from enum import Enum
from typing import override


class TextType(Enum):
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


class HTMLNode:
    def __init__(
        self,
        tag: str | None = None,
        value: str | None = None,
        children: list[HTMLNode] | None = None,
        props: dict[str, str] | None = None,
    ) -> None:
        self.tag: str | None = tag
        self.value: str | None = value
        self.children: list[HTMLNode] | None = children
        self.props: dict[str, str] | None = props

    def to_dict(self) -> dict:
        """Create a dict representation of self."""
        return {
            "class": type(self).__name__,
            "tag": self.tag or "None",
            "value": self.value or "None",
            "children": [x.to_dict() for x in self.children]
            if self.children is not None
            else "None",
            "props": self.props or "None",
        }

    def __repr__(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def to_html(self) -> str:
        raise NotImplementedError

    def props_to_html(self) -> str:
        if self.props is None:
            return ""

        html_parts: list[str] = []
        for k, v in self.props.items():
            html_parts.append(f'{k}="{v}"')

        return " ".join(html_parts)


class HTMLLeafNode(HTMLNode):
    def __init__(
        self,
        tag: str | None,
        value: str | None,
        props: dict[str, str] | None = None,
    ) -> None:
        super().__init__(tag=tag, value=value, props=props)

    @override
    def to_html(self) -> str:
        """Construct a valid html string from self.

        Examples:
            `LeafNode("p", "This is a paragraph of text.").to_html()`
            `> "<p>This is a paragraph of text.</p>"`

            `ALeafNode("a", "Click me!", {"href": "https://www.google.com"}).to_html()`
            `> '<a href="https://www.google.com">Click me!</a>'`
        """
        if not self.value or self.value is None:
            msg = "No value set, leaf nodes must have a value"
            raise ValueError(msg)

        if self.tag is None:
            return self.value

        html_props = self.props_to_html()
        start_tag = f"<{self.tag} {html_props}>" if html_props else f"<{self.tag}>"
        end_tag = f"</{self.tag}>"

        return f"{start_tag}{self.value}{end_tag}"


class HTMLParentNode(HTMLNode):
    def __init__(
        self,
        tag: str,
        children: list[HTMLNode],
        props: dict[str, str] | None = None,
    ) -> None:
        super().__init__(tag=tag, children=children, props=props)

    @override
    def to_html(self) -> str:
        """Construct a valid html string from self."""
        if not self.tag:
            msg = "No tag set, parent nodes must have a tag"
            raise ValueError(msg)

        if not self.children:
            msg = "No child nodes, parent nodes must have children"
            raise ValueError(msg)

        html_props = self.props_to_html()
        start_tag = f"<{self.tag} {html_props}>" if html_props else f"<{self.tag}>"
        end_tag = f"</{self.tag}>"
        body = "".join([x.to_html() for x in self.children])

        return f"{start_tag}{body}{end_tag}"


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
