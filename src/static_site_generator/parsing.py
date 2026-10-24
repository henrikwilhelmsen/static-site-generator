# Copyright (C) 2026 Henrik Wilhelmsen.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at <https://mozilla.org/MPL/2.0/>.

import re
from typing import TYPE_CHECKING, Literal

from static_site_generator.models import (
    BlockType,
    HTMLLeafNode,
    HTMLNode,
    HTMLParentNode,
    TextNode,
    TextType,
)

if TYPE_CHECKING:
    from pathlib import Path


def text_node_to_html_node(text_node: TextNode) -> HTMLNode:
    match text_node.text_type:
        case TextType.TEXT:
            return HTMLLeafNode(tag=None, value=text_node.text)
        case TextType.BOLD:
            return HTMLLeafNode(tag="b", value=text_node.text)
        case TextType.ITALIC:
            return HTMLLeafNode(tag="i", value=text_node.text)
        case TextType.CODE:
            return HTMLLeafNode(tag="code", value=text_node.text)
        case TextType.LINK:
            if text_node.url is None:
                msg = "Link text node is missing a URL"
                raise ValueError(msg)

            return HTMLLeafNode(
                tag="a",
                value=text_node.text,
                props={"href": text_node.url},
            )
        case TextType.IMAGE:
            if text_node.url is None:
                msg = "Image text node is missing a URL"
                raise ValueError(msg)

            return HTMLLeafNode(
                tag="img",
                value=text_node.text,
                props={"src": text_node.url},
            )
        case _:
            msg = f"Invalid text type for node '{text_node}'"
            raise ValueError


def extract_markdown_images(text: str) -> list[tuple[str, str]]:
    """Extract any markdown images from the given string.

    Returns a list of tuples `(image_text, image_url)`.
    """
    # Match on '![any text](any text)'
    pattern = r"!\[([^\[\]]*)\]\(([^\(\)]*)\)"
    return re.findall(pattern, text)


def extract_markdown_links(text: str) -> list[tuple[str, str]]:
    """Extract any markdown links from the given string.

    Returns a list of tuples `(link_text, link_url)`.
    """
    # Same pattern as for images, but specifically checking that there is no leading '!'
    pattern = r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)"
    return re.findall(pattern, text)


def split_nodes_delimiter(
    old_nodes: list[TextNode],
    delimiter: str,
    text_type: TextType,
) -> list[TextNode]:
    """Split the given list of nodes on the given delimiter and return the new nodes.

    Note: Currently not handling nested delimiters and italics should be limited to `_`
    as we do not handle text with both `**bold**` and `*italic*`, since we just split
    the text on the given delimiter using `.split()`.
    """
    new_nodes: list[TextNode] = []
    for old_node in old_nodes:
        # Skip nodes that are not text nodes
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue

        if delimiter not in old_node.text:
            new_nodes.append(old_node)
            continue

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


def split_nodes_url_type(
    old_nodes: list[TextNode],
    url_type: Literal[TextType.LINK, TextType.IMAGE],
) -> list[TextNode]:
    """Split the given list of nodes into nodes with url, either images or links."""
    match url_type:
        case TextType.LINK:
            extraction_fn = extract_markdown_links
            split_prefix = ""
        case TextType.IMAGE:
            extraction_fn = extract_markdown_images
            split_prefix = "!"

    new_nodes: list[TextNode] = []
    for node in old_nodes:
        # Leave any nodes that are not pure text
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        # Extract any images. Append current node and continue if there are none.
        extracted_parts = extraction_fn(node.text)
        if not extracted_parts:
            new_nodes.append(node)
            continue

        sub_nodes: list[TextNode] = []
        text: str = node.text
        for alt_text, url in extracted_parts:
            # Split the text on the url, so we get the text before and after it
            sections = text.split(f"{split_prefix}[{alt_text}]({url})", 1)
            start_text = sections[0]
            end_text = sections[1]

            # Append the start text if there is any
            if start_text:
                sub_nodes.append(TextNode(text=start_text, text_type=TextType.TEXT))

            # Append the url node
            sub_nodes.append(TextNode(text=alt_text, text_type=url_type, url=url))

            # Update text with the remainder so we can extract any other urls
            text = end_text

        # Append any remaining text as a text node
        if text:
            sub_nodes.append(TextNode(text=text, text_type=TextType.TEXT))

        new_nodes.extend(sub_nodes)
    return new_nodes


def split_nodes_link(
    old_nodes: list[TextNode],
) -> list[TextNode]:
    """Split any nodes in the given list containing links into text and link nodes.

    Returns a new list of nodes where any text node containing a link has been split
    into text nodes and link nodes.
    """
    return split_nodes_url_type(old_nodes=old_nodes, url_type=TextType.LINK)


def split_nodes_image(
    old_nodes: list[TextNode],
) -> list[TextNode]:
    """Split any nodes in the given list containing images into text and image nodes.

    Returns a new list of nodes where any text node containing an image has been split
    into text nodes and image nodes.
    """
    return split_nodes_url_type(old_nodes=old_nodes, url_type=TextType.IMAGE)


def text_to_text_nodes(text: str) -> list[TextNode]:
    """Parse the given text into a list of TextNodes."""
    nodes: list[TextNode] = [TextNode(text=text, text_type=TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    return split_nodes_link(nodes)


def markdown_to_blocks(markdown: str) -> list[str]:
    """Split the given document on double newline to get a list of text blocks."""
    blocks = [x.strip() for x in markdown.split("\n\n")]
    return [x for x in blocks if x]


def block_to_block_type(block: str) -> BlockType:
    """Return the block type of the given block of markdown text.

    Assumes that all leading and trailing whitespace has been removed.
    """
    lines = block.splitlines()

    # Headings start with 1-6 # and a space
    heading_pattern = re.compile(r"^#{1,6} ")
    if heading_pattern.match(block) is not None:
        return BlockType.HEADING

    # Code starts and ends with three backticks `
    if block.startswith("```") and block.endswith("```"):
        return BlockType.CODE

    # Every line in a quote block must start with >
    if all(line.startswith(">") for line in lines):
        return BlockType.QUOTE

    # Every line in an unordered list must start with -
    if all(line.startswith("-") for line in lines):
        return BlockType.UNORDERED_LIST

    # Every line in an ordered list must start with a number followed by a . and a space
    ordered_list_pattern = re.compile(r"^\d+\. ")
    if ordered_list_pattern.match(block) is not None:
        return BlockType.ORDERED_LIST

    # No matches to above rules, block is a paragraph
    return BlockType.PARAGRAPH


def text_to_children(text: str) -> list[HTMLNode]:
    """Convert the given text to a list of html nodes."""
    text_nodes = text_to_text_nodes(text)
    return [text_node_to_html_node(x) for x in text_nodes]


def markdown_to_html_node(markdown: str) -> HTMLNode:
    """Convert the given markdown document to an html node."""
    blocks = markdown_to_blocks(markdown)
    root_children: list[HTMLNode] = []

    for block in blocks:
        block_type = block_to_block_type(block)
        match block_type:
            case BlockType.HEADING:
                heading_split = block.split(" ", maxsplit=1)
                root_children.append(
                    HTMLParentNode(
                        tag=f"h{heading_split[0].count('#')}",
                        children=text_to_children(heading_split[1]),
                    ),
                )

            case BlockType.CODE:
                code_body = block.removeprefix("```").removesuffix("```")
                text_node = TextNode(text=code_body, text_type=TextType.CODE)
                root_children.append(
                    HTMLParentNode(
                        tag="pre",
                        children=[text_node_to_html_node(text_node)],
                    ),
                )

            case BlockType.QUOTE:
                quote_body = " ".join(
                    [x.removeprefix(">").strip() for x in block.splitlines()],
                )
                root_children.append(
                    HTMLParentNode(
                        tag="blockquote",
                        children=text_to_children(quote_body),
                    ),
                )

            case BlockType.UNORDERED_LIST:
                list_items = [x.removeprefix("-").strip() for x in block.splitlines()]
                root_children.append(
                    HTMLParentNode(
                        tag="ul",
                        children=[
                            HTMLParentNode(
                                tag="li",
                                children=text_to_children(x),
                            )
                            for x in list_items
                        ],
                    ),
                )

            case BlockType.ORDERED_LIST:
                list_items = [
                    x.split(" ", maxsplit=1)[1].strip() for x in block.splitlines()
                ]
                root_children.append(
                    HTMLParentNode(
                        tag="ol",
                        children=[
                            HTMLParentNode(
                                tag="li",
                                children=text_to_children(x),
                            )
                            for x in list_items
                        ],
                    ),
                )

            case BlockType.PARAGRAPH:
                root_children.append(
                    HTMLParentNode(
                        tag="p",
                        children=text_to_children(" ".join(block.splitlines())),
                    ),
                )

    return HTMLParentNode(tag="div", children=root_children)


def extract_title(markdown: str) -> str:
    title_lines = [x for x in markdown.splitlines() if x.startswith("# ")]
    if not title_lines:
        msg = "Markdown does not contain a title"
        raise ValueError(msg)

    return title_lines[0].split(" ", maxsplit=1)[1].strip()


def generate_page(
    source_dir: Path,
    target_dir: Path,
    template_file: Path,
    basepath: str = "/",
) -> None:
    print(
        f"Generating page from '{source_dir}' to '{target_dir}' using '{template_file}'",  # noqa: E501
    )
    source_md = source_dir.read_text(encoding="utf-8")
    source_html = markdown_to_html_node(source_md).to_html()
    source_title = extract_title(source_md)
    template_html = template_file.read_text(encoding="utf-8")
    target_html = template_html.replace("{{ Title }}", source_title).replace(
        "{{ Content }}",
        source_html,
    )

    if basepath != "/":
        target_html = target_html.replace('href="/', f'href="{basepath}').replace(
            'src="/',
            f'src="{basepath}',
        )

    if not target_dir.parent.exists():
        target_dir.parent.mkdir(parents=True)

    target_dir.write_text(target_html)


def generate_pages(
    source_dir: Path,
    target_dir: Path,
    template_file: Path,
    basepath: str,
) -> None:
    for md_file in source_dir.rglob("*.md"):
        generate_page(
            source_dir=md_file,
            target_dir=target_dir
            / md_file.relative_to(source_dir).parent
            / f"{md_file.stem}.html",
            template_file=template_file,
            basepath=basepath,
        )
