import json
from enum import Enum


class TextType(Enum):
    PLAIN = "plain"
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
