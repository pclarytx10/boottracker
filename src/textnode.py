from enum import Enum
import re

class TextType(Enum):
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"


class TextNode:
    def __init__(self, text, text_type, url=None):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other):
        return (
            self.text == other.text
            and self.text_type == other.text_type
            and self.url == other.url
        )

    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type}, {self.url})"


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
            
        parts = node.text.split(delimiter)
        
        if len(parts) % 2 == 0:
            raise ValueError(f"Invalid markdown, formatted section not closed")
        
        for i, part in enumerate(parts):
            if i % 2 == 0:
                if part != "":
                    new_nodes.append(TextNode(part, TextType.TEXT))
            else:
                if part != "":
                    new_nodes.append(TextNode(part, text_type))
    
    return new_nodes


def extract_markdown_images(text):
    pattern = r"!\[([^\[\]]*?)\]\(([^\(\)]*?)\)"
    matches = re.findall(pattern, text)
    return matches


def extract_markdown_links(text):
    pattern = r"(?<!!)\[([^\[\]]*?)\]\(([^\(\)]*?)\)"
    matches = re.findall(pattern, text)
    return matches

