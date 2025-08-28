from enum import Enum
import re
import os

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


def markdown_to_blocks(markdown):
    lines = markdown.split('\n')
    blocks = []
    current_block = []
    
    for line in lines:
        stripped_line = line.strip()
        
        # If we encounter an empty line and we have content in current_block
        if not stripped_line and current_block:
            # Join the current block and add it to blocks
            blocks.append('\n'.join(current_block))
            current_block = []
        elif stripped_line:
            # Add non-empty line to current block
            current_block.append(line)
    
    # Don't forget the last block if there's content
    if current_block:
        blocks.append('\n'.join(current_block))
    
    # Clean up blocks (remove leading/trailing whitespace)
    result = []
    for block in blocks:
        stripped_block = block.strip()
        if stripped_block:
            result.append(stripped_block)
    
    return result


def block_to_block_type(block):
    lines = block.split('\n')
    
    # Check for heading
    if block.startswith(('# ', '## ', '### ', '#### ', '##### ', '###### ')):
        return BlockType.HEADING
    
    # Check for code block
    if block.startswith('```') and block.endswith('```') and len(block) > 6:
        return BlockType.CODE
    
    # Check for quote block
    if all(line.startswith('> ') or line == '>' for line in lines):
        return BlockType.QUOTE
    
    # Check for unordered list
    if all(line.startswith('- ') for line in lines):
        return BlockType.UNORDERED_LIST
    
    # Check for ordered list
    if len(lines) > 0:
        is_ordered_list = True
        for i, line in enumerate(lines):
            expected_number = str(i + 1) + '. '
            if not line.startswith(expected_number):
                is_ordered_list = False
                break
        if is_ordered_list:
            return BlockType.ORDERED_LIST
    
    # Default to paragraph
    return BlockType.PARAGRAPH


def text_to_children(text):
    try:
        from htmlnode import text_node_to_html_node
    except ImportError:
        from .htmlnode import text_node_to_html_node
    
    text_nodes = text_to_textnodes(text)
    children = []
    
    for text_node in text_nodes:
        html_node = text_node_to_html_node(text_node)
        children.append(html_node)
    
    return children


def extract_title(markdown):
    lines = markdown.split('\n')
    
    for line in lines:
        stripped_line = line.strip()
        
        # Check if line starts with exactly "# " (h1) and not "## " (h2+)
        if stripped_line.startswith('# ') and not stripped_line.startswith('## '):
            return stripped_line[2:].strip()
        # Handle edge case: "# " becomes "#" after stripping
        elif stripped_line == '#' and line.endswith(' '):
            return ""
    
    raise ValueError("No h1 header found in markdown")


def generate_page(from_path, template_path, dest_path, basepath="/"):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    
    # Read the markdown file
    with open(from_path, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # Read the template file
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Convert markdown to HTML
    html_node = markdown_to_html_node(markdown_content)
    html_content = html_node.to_html()
    
    # Extract the title
    title = extract_title(markdown_content)
    
    # Replace placeholders in template
    final_html = template_content.replace('{{ Title }}', title)
    final_html = final_html.replace('{{ Content }}', html_content)
    
    # Replace href="/ and src="/ with basepath
    final_html = final_html.replace('href="/', f'href="{basepath}')
    final_html = final_html.replace('src="/', f'src="{basepath}')
    
    # Create destination directory if it doesn't exist
    dest_dir = os.path.dirname(dest_path)
    if dest_dir and not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    
    # Write the final HTML to the destination file
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(final_html)


def markdown_to_html_node(markdown):
    try:
        from htmlnode import ParentNode, text_node_to_html_node
    except ImportError:
        from .htmlnode import ParentNode, text_node_to_html_node
    
    blocks = markdown_to_blocks(markdown)
    block_nodes = []
    
    for block in blocks:
        block_type = block_to_block_type(block)
        
        if block_type == BlockType.PARAGRAPH:
            # Replace newlines with spaces in paragraphs
            paragraph_text = block.replace('\n', ' ')
            children = text_to_children(paragraph_text)
            block_nodes.append(ParentNode("p", children))
            
        elif block_type == BlockType.HEADING:
            # Count the number of # characters
            level = 0
            for char in block:
                if char == '#':
                    level += 1
                else:
                    break
            
            # Extract heading text after "# "
            heading_text = block[level+1:]  # Skip the # characters and space
            children = text_to_children(heading_text)
            block_nodes.append(ParentNode(f"h{level}", children))
            
        elif block_type == BlockType.CODE:
            # Extract code content by finding first and last ``` positions
            first_newline = block.find('\n')
            last_backticks = block.rfind('```')
            
            if first_newline != -1 and last_backticks > first_newline:
                # Extract everything between the first newline and the last ```
                code_content = block[first_newline + 1:last_backticks]
            else:
                code_content = ""
            
            # Create text node without inline parsing
            code_text_node = TextNode(code_content, TextType.TEXT)
            code_html_node = text_node_to_html_node(code_text_node)
            
            # Wrap in pre > code
            code_parent = ParentNode("code", [code_html_node])
            block_nodes.append(ParentNode("pre", [code_parent]))
            
        elif block_type == BlockType.QUOTE:
            # Extract quote content (remove ">" from each line)
            lines = block.split('\n')
            quote_lines = []
            for line in lines:
                if line.startswith('> '):
                    quote_lines.append(line[2:])  # Remove "> "
                elif line.startswith('>'):
                    quote_lines.append(line[1:])  # Remove ">"
                else:
                    quote_lines.append(line)  # Keep as is
            quote_text = '\n'.join(quote_lines)
            
            children = text_to_children(quote_text)
            block_nodes.append(ParentNode("blockquote", children))
            
        elif block_type == BlockType.UNORDERED_LIST:
            # Extract list items (remove "- " from each line)
            lines = block.split('\n')
            list_items = []
            for line in lines:
                item_text = line[2:]  # Remove "- "
                item_children = text_to_children(item_text)
                list_items.append(ParentNode("li", item_children))
            
            block_nodes.append(ParentNode("ul", list_items))
            
        elif block_type == BlockType.ORDERED_LIST:
            # Extract list items (remove "1. ", "2. ", etc. from each line)
            lines = block.split('\n')
            list_items = []
            for line in lines:
                # Find the first space after the number and period
                dot_index = line.find('. ')
                item_text = line[dot_index + 2:]  # Remove "1. " etc.
                item_children = text_to_children(item_text)
                list_items.append(ParentNode("li", item_children))
            
            block_nodes.append(ParentNode("ol", list_items))
    
    # Wrap all block nodes in a div
    return ParentNode("div", block_nodes)


def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath="/"):
    """
    Recursively crawl the content directory and generate HTML pages for all markdown files.
    
    Args:
        dir_path_content: Path to the content directory
        template_path: Path to the HTML template file
        dest_dir_path: Path to the destination directory for generated HTML files
        basepath: Base path for the site (defaults to "/")
    """
    print(f"Generating pages recursively from {dir_path_content} to {dest_dir_path}")
    
    # Create destination directory if it doesn't exist
    if not os.path.exists(dest_dir_path):
        os.makedirs(dest_dir_path)
    
    # Walk through the content directory
    for root, dirs, files in os.walk(dir_path_content):
        # Calculate the relative path from content directory
        rel_path = os.path.relpath(root, dir_path_content)
        
        # Create corresponding directory in destination
        dest_subdir = os.path.join(dest_dir_path, rel_path)
        if rel_path != '.' and not os.path.exists(dest_subdir):
            os.makedirs(dest_subdir)
        
        # Process each file in the current directory
        for file in files:
            if file.endswith('.md'):
                # Source markdown file path
                source_path = os.path.join(root, file)
                
                # Destination HTML file path (replace .md with .html)
                html_filename = file.replace('.md', '.html')
                dest_path = os.path.join(dest_subdir, html_filename)
                
                # Generate the HTML page
                generate_page(source_path, template_path, dest_path, basepath)