import json
from typing import override


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

    def _to_dict(self) -> dict:
        """Create a dict representation of self for readability with json.dumps."""
        return {
            "class": type(self).__name__,
            "tag": self.tag or "None",
            "value": self.value or "None",
            "children": [x._to_dict() for x in self.children]  # noqa: SLF001
            if self.children is not None
            else "None",
            "props": self.props or "None",
        }

    def __repr__(self) -> str:
        return json.dumps(self._to_dict(), indent=2)

    def to_html(self) -> str:
        raise NotImplementedError

    def props_to_html(self) -> str:
        if self.props is None:
            return ""

        html_parts: list[str] = []
        for k, v in self.props.items():
            html_parts.append(f'{k}="{v}"')

        return " ".join(html_parts)


class LeafNode(HTMLNode):
    def __init__(
        self,
        tag: str | None,
        value: str | None,
        props: dict[str, str] | None = None,
    ) -> None:
        super().__init__(tag=tag, value=value, props=props)

    @override
    def _to_dict(self) -> dict:
        """Create a dict representation of self for readability with json.dumps.

        Override with children removed, since leaf nodes have no children.
        """
        return {
            "class": type(self).__name__,
            "tag": self.tag or "None",
            "value": self.value or "None",
            "props": self.props or "None",
        }

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
