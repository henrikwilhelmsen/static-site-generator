import re

from static_site_generator.text_node import TextNode, TextType


def split_nodes_delimiter(
    old_nodes: list[TextNode],
    delimiter: str,
    text_type: TextType,
) -> list[TextNode]:
    """Split the given list of nodes on the given delimiter and return the new nodes.

    Note: Currently not handling nested delimiters and italics should be limited to `_`
    as we do not handle text with both `**bold**` and `*italic*`, sinc we just split
    the text on the given delimiter using `.split()`.
    """
    new_nodes: list[TextNode] = []
    for old_node in old_nodes:
        # Skip nodes that are not text nodes
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue

        if delimiter not in old_node.text:
            msg = f"No delimiter '{delimiter}' in text '{old_node.text}'"
            raise ValueError(msg)

        # If we have an uneven amount of delimiters, we are missing a closing one.
        if old_node.text.count(delimiter) % 2 != 0:
            msg = f"Invalid markdown syntax, text is missing a closing '{delimiter}': "
            f"'{old_node.text}'"
            raise ValueError(msg)

        # When splitting on an even number of delimiters, text at the odd index should
        # be inside the delimiter and of the new text type while even indexes are plain
        # text.
        split_text = old_node.text.split(delimiter)
        for i, t in enumerate(split_text):
            if not t:
                continue
            if i % 2 == 0:
                new_nodes.append(TextNode(text=t, text_type=TextType.TEXT))
            else:
                new_nodes.append(TextNode(text=t, text_type=text_type))

    return new_nodes


def extract_markdown_images(text: str) -> list[tuple[str]]:
    # Match on '![any text](any text)'
    pattern = r"!\[([^\[\]]*)\]\(([^\(\)]*)\)"
    return re.findall(pattern, text)


def extract_markdown_links(text: str) -> list[tuple[str]]:
    # Same pattern as for images, but specifically checking that there is no leading '!'
    pattern = r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)"
    return re.findall(pattern, text)
