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


def split_nodes_image(old_nodes):
    new_nodes = []
    
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        
        images = extract_markdown_images(node.text)
        if not images:
            new_nodes.append(node)
            continue
        
        current_text = node.text
        for alt_text, url in images:
            image_markdown = f"![{alt_text}]({url})"
            parts = current_text.split(image_markdown, 1)
            
            if len(parts) != 2:
                continue
            
            before_text = parts[0]
            if before_text:
                new_nodes.append(TextNode(before_text, TextType.TEXT))
            
            new_nodes.append(TextNode(alt_text, TextType.IMAGE, url))
            
            current_text = parts[1]
        
        if current_text:
            new_nodes.append(TextNode(current_text, TextType.TEXT))
    
    return new_nodes


def split_nodes_link(old_nodes):
    new_nodes = []
    
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        
        links = extract_markdown_links(node.text)
        if not links:
            new_nodes.append(node)
            continue
        
        current_text = node.text
        for link_text, url in links:
            link_markdown = f"[{link_text}]({url})"
            parts = current_text.split(link_markdown, 1)
            
            if len(parts) != 2:
                continue
            
            before_text = parts[0]
            if before_text:
                new_nodes.append(TextNode(before_text, TextType.TEXT))
            
            new_nodes.append(TextNode(link_text, TextType.LINK, url))
            
            current_text = parts[1]
        
        if current_text:
            new_nodes.append(TextNode(current_text, TextType.TEXT))
    
    return new_nodes


def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes