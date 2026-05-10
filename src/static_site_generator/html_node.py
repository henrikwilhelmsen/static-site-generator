import json


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

    def to_html(self) -> None:
        raise NotImplementedError

    def props_to_html(self) -> str:
        if self.props is None:
            return ""

        html_parts: list[str] = []
        for k, v in self.props.items():
            html_parts.append(f'{k}="{v}"')

        return " ".join(html_parts)
