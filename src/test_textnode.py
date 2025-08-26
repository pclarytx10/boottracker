import unittest

from textnode import TextNode, TextType, BlockType, split_nodes_delimiter, extract_markdown_images, extract_markdown_links, split_nodes_image, split_nodes_link, text_to_textnodes, markdown_to_blocks, block_to_block_type, text_to_children, markdown_to_html_node


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_not_equal_text(self):
        node1 = TextNode("Text 1", TextType.BOLD)
        node2 = TextNode("Text 2", TextType.BOLD)
        self.assertNotEqual(node1, node2)

    def test_not_equal_type(self):
        node1 = TextNode("Same text", TextType.BOLD)
        node2 = TextNode("Same text", TextType.ITALIC)
        self.assertNotEqual(node1, node2)

    def test_not_equal_url(self):
        node1 = TextNode("Text", TextType.LINK, url="http://a.com")
        node2 = TextNode("Text", TextType.LINK, url="http://b.com")
        self.assertNotEqual(node1, node2)

    def test_equal_with_url(self):
        node1 = TextNode("Text", TextType.LINK, url="http://a.com")
        node2 = TextNode("Text", TextType.LINK, url="http://a.com")
        self.assertEqual(node1, node2)


class TestSplitNodesDelimiter(unittest.TestCase):
    def test_split_code_delimiter(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" word", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_bold_delimiter(self):
        node = TextNode("This is **bold** text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_italic_delimiter(self):
        node = TextNode("This is *italic* text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "*", TextType.ITALIC)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_multiple_delimiters(self):
        node = TextNode("Code `here` and `there` in text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("Code ", TextType.TEXT),
            TextNode("here", TextType.CODE),
            TextNode(" and ", TextType.TEXT),
            TextNode("there", TextType.CODE),
            TextNode(" in text", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_no_delimiter(self):
        node = TextNode("This is plain text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [TextNode("This is plain text", TextType.TEXT)]
        self.assertEqual(new_nodes, expected)

    def test_split_entire_text_formatted(self):
        node = TextNode("`entire text is code`", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [TextNode("entire text is code", TextType.CODE)]
        self.assertEqual(new_nodes, expected)

    def test_split_starts_with_delimiter(self):
        node = TextNode("`code` at the start", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("code", TextType.CODE),
            TextNode(" at the start", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_ends_with_delimiter(self):
        node = TextNode("Text ends with `code`", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("Text ends with ", TextType.TEXT),
            TextNode("code", TextType.CODE),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_empty_delimiter_content(self):
        node = TextNode("Text with `` empty code", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("Text with ", TextType.TEXT),
            TextNode(" empty code", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_non_text_nodes_unchanged(self):
        nodes = [
            TextNode("Plain text", TextType.TEXT),
            TextNode("Bold text", TextType.BOLD),
            TextNode("Code text", TextType.CODE),
        ]
        new_nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
        expected = [
            TextNode("Plain text", TextType.TEXT),
            TextNode("Bold text", TextType.BOLD),
            TextNode("Code text", TextType.CODE),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_mixed_node_types(self):
        nodes = [
            TextNode("Text with `code` here", TextType.TEXT),
            TextNode("Already bold", TextType.BOLD),
            TextNode("More `code` text", TextType.TEXT),
        ]
        new_nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
        expected = [
            TextNode("Text with ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" here", TextType.TEXT),
            TextNode("Already bold", TextType.BOLD),
            TextNode("More ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_unclosed_delimiter_raises_exception(self):
        node = TextNode("This has `unclosed code", TextType.TEXT)
        with self.assertRaises(ValueError) as context:
            split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertIn("Invalid markdown, formatted section not closed", str(context.exception))

    def test_three_delimiters_raises_exception(self):
        node = TextNode("Text `code` more `unclosed", TextType.TEXT)
        with self.assertRaises(ValueError) as context:
            split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertIn("Invalid markdown, formatted section not closed", str(context.exception))

    def test_underscore_italic_delimiter(self):
        node = TextNode("This is _italic_ text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "_", TextType.ITALIC)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_double_asterisk_bold_delimiter(self):
        node = TextNode("This is **very bold** text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("very bold", TextType.BOLD),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_complex_mixed_delimiters(self):
        node = TextNode("Start `code` middle **bold** end", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        intermediate = [
            TextNode("Start ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" middle **bold** end", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, intermediate)
        
        final_nodes = split_nodes_delimiter(new_nodes, "**", TextType.BOLD)
        expected = [
            TextNode("Start ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" middle ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" end", TextType.TEXT),
        ]
        self.assertEqual(final_nodes, expected)


class TestExtractMarkdownImages(unittest.TestCase):
    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_markdown_images_multiple(self):
        text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        matches = extract_markdown_images(text)
        expected = [("rick roll", "https://i.imgur.com/aKaOqIh.gif"), ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg")]
        self.assertListEqual(expected, matches)

    def test_extract_markdown_images_no_images(self):
        text = "This is text with no images"
        matches = extract_markdown_images(text)
        self.assertListEqual([], matches)

    def test_extract_markdown_images_empty_alt(self):
        text = "Image with empty alt ![](https://example.com/image.png)"
        matches = extract_markdown_images(text)
        self.assertListEqual([("", "https://example.com/image.png")], matches)

    def test_extract_markdown_images_complex_alt(self):
        text = "Image with ![complex alt text with spaces](https://example.com/image.png)"
        matches = extract_markdown_images(text)
        self.assertListEqual([("complex alt text with spaces", "https://example.com/image.png")], matches)

    def test_extract_markdown_images_ignores_links(self):
        text = "This has a [link](https://example.com) and ![image](https://example.com/img.png)"
        matches = extract_markdown_images(text)
        self.assertListEqual([("image", "https://example.com/img.png")], matches)


class TestExtractMarkdownLinks(unittest.TestCase):
    def test_extract_markdown_links(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        matches = extract_markdown_links(text)
        expected = [("to boot dev", "https://www.boot.dev"), ("to youtube", "https://www.youtube.com/@bootdotdev")]
        self.assertListEqual(expected, matches)

    def test_extract_markdown_links_single(self):
        text = "Check out [this link](https://example.com)"
        matches = extract_markdown_links(text)
        self.assertListEqual([("this link", "https://example.com")], matches)

    def test_extract_markdown_links_no_links(self):
        text = "This text has no links"
        matches = extract_markdown_links(text)
        self.assertListEqual([], matches)

    def test_extract_markdown_links_empty_text(self):
        text = "Link with empty text [](https://example.com)"
        matches = extract_markdown_links(text)
        self.assertListEqual([("", "https://example.com")], matches)

    def test_extract_markdown_links_complex_text(self):
        text = "Link with [complex link text with spaces](https://example.com/path)"
        matches = extract_markdown_links(text)
        self.assertListEqual([("complex link text with spaces", "https://example.com/path")], matches)

    def test_extract_markdown_links_ignores_images(self):
        text = "This has an ![image](https://example.com/img.png) and [link](https://example.com)"
        matches = extract_markdown_links(text)
        self.assertListEqual([("link", "https://example.com")], matches)

    def test_extract_markdown_links_multiple_on_same_line(self):
        text = "Multiple [link1](https://one.com) and [link2](https://two.com) links"
        matches = extract_markdown_links(text)
        expected = [("link1", "https://one.com"), ("link2", "https://two.com")]
        self.assertListEqual(expected, matches)

    def test_extract_markdown_links_with_special_chars(self):
        text = "Link with [special & chars!](https://example.com?param=value&other=123)"
        matches = extract_markdown_links(text)
        self.assertListEqual([("special & chars!", "https://example.com?param=value&other=123")], matches)


class TestSplitNodesImage(unittest.TestCase):
    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_images_single(self):
        node = TextNode("Here is an ![alt text](https://example.com/image.png)", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("Here is an ", TextType.TEXT),
            TextNode("alt text", TextType.IMAGE, "https://example.com/image.png"),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_images_no_images(self):
        node = TextNode("This text has no images at all", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = [TextNode("This text has no images at all", TextType.TEXT)]
        self.assertEqual(new_nodes, expected)

    def test_split_images_empty_alt_text(self):
        node = TextNode("Image with ![](https://example.com/img.png) empty alt", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("Image with ", TextType.TEXT),
            TextNode("", TextType.IMAGE, "https://example.com/img.png"),
            TextNode(" empty alt", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_images_at_start(self):
        node = TextNode("![first image](https://example.com/start.png) text after", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("first image", TextType.IMAGE, "https://example.com/start.png"),
            TextNode(" text after", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_images_at_end(self):
        node = TextNode("Text before ![last image](https://example.com/end.png)", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("Text before ", TextType.TEXT),
            TextNode("last image", TextType.IMAGE, "https://example.com/end.png"),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_images_entire_text(self):
        node = TextNode("![whole thing](https://example.com/whole.png)", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = [TextNode("whole thing", TextType.IMAGE, "https://example.com/whole.png")]
        self.assertEqual(new_nodes, expected)

    def test_split_images_consecutive(self):
        node = TextNode("![first](https://example.com/1.png)![second](https://example.com/2.png)", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("first", TextType.IMAGE, "https://example.com/1.png"),
            TextNode("second", TextType.IMAGE, "https://example.com/2.png"),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_images_multiple_scattered(self):
        node = TextNode("Start ![img1](https://a.com/1.png) middle ![img2](https://b.com/2.png) end", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("Start ", TextType.TEXT),
            TextNode("img1", TextType.IMAGE, "https://a.com/1.png"),
            TextNode(" middle ", TextType.TEXT),
            TextNode("img2", TextType.IMAGE, "https://b.com/2.png"),
            TextNode(" end", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_images_with_complex_urls(self):
        node = TextNode("Image ![complex](https://example.com/path/to/image.png?param=value&size=large) here", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("Image ", TextType.TEXT),
            TextNode("complex", TextType.IMAGE, "https://example.com/path/to/image.png?param=value&size=large"),
            TextNode(" here", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_images_non_text_nodes_unchanged(self):
        nodes = [
            TextNode("Text with ![image](https://example.com/img.png)", TextType.TEXT),
            TextNode("Bold text", TextType.BOLD),
            TextNode("Code text", TextType.CODE),
        ]
        new_nodes = split_nodes_image(nodes)
        expected = [
            TextNode("Text with ", TextType.TEXT),
            TextNode("image", TextType.IMAGE, "https://example.com/img.png"),
            TextNode("Bold text", TextType.BOLD),
            TextNode("Code text", TextType.CODE),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_images_mixed_with_existing_image_nodes(self):
        nodes = [
            TextNode("Text with ![new image](https://example.com/new.png)", TextType.TEXT),
            TextNode("existing image", TextType.IMAGE, "https://example.com/existing.png"),
        ]
        new_nodes = split_nodes_image(nodes)
        expected = [
            TextNode("Text with ", TextType.TEXT),
            TextNode("new image", TextType.IMAGE, "https://example.com/new.png"),
            TextNode("existing image", TextType.IMAGE, "https://example.com/existing.png"),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_images_ignores_links(self):
        node = TextNode("Text with [link](https://example.com) and ![image](https://example.com/img.png)", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("Text with [link](https://example.com) and ", TextType.TEXT),
            TextNode("image", TextType.IMAGE, "https://example.com/img.png"),
        ]
        self.assertEqual(new_nodes, expected)


class TestSplitNodesLink(unittest.TestCase):
    def test_split_links(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("This is text with a link ", TextType.TEXT),
            TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
            TextNode(" and ", TextType.TEXT),
            TextNode("to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_links_single(self):
        node = TextNode("Check out [this awesome site](https://example.com)", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("Check out ", TextType.TEXT),
            TextNode("this awesome site", TextType.LINK, "https://example.com"),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_links_no_links(self):
        node = TextNode("This text has no links at all", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [TextNode("This text has no links at all", TextType.TEXT)]
        self.assertEqual(new_nodes, expected)

    def test_split_links_empty_text(self):
        node = TextNode("Link with [](https://example.com) empty text", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("Link with ", TextType.TEXT),
            TextNode("", TextType.LINK, "https://example.com"),
            TextNode(" empty text", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_links_at_start(self):
        node = TextNode("[first link](https://example.com/start) text after", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("first link", TextType.LINK, "https://example.com/start"),
            TextNode(" text after", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_links_at_end(self):
        node = TextNode("Text before [last link](https://example.com/end)", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("Text before ", TextType.TEXT),
            TextNode("last link", TextType.LINK, "https://example.com/end"),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_links_entire_text(self):
        node = TextNode("[whole thing](https://example.com/whole)", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [TextNode("whole thing", TextType.LINK, "https://example.com/whole")]
        self.assertEqual(new_nodes, expected)

    def test_split_links_consecutive(self):
        node = TextNode("[first](https://example.com/1)[second](https://example.com/2)", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("first", TextType.LINK, "https://example.com/1"),
            TextNode("second", TextType.LINK, "https://example.com/2"),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_links_multiple_scattered(self):
        node = TextNode("Start [link1](https://a.com) middle [link2](https://b.com) end", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("Start ", TextType.TEXT),
            TextNode("link1", TextType.LINK, "https://a.com"),
            TextNode(" middle ", TextType.TEXT),
            TextNode("link2", TextType.LINK, "https://b.com"),
            TextNode(" end", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_links_with_complex_urls(self):
        node = TextNode("Link [complex](https://example.com/path/to/page?param=value&size=large) here", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("Link ", TextType.TEXT),
            TextNode("complex", TextType.LINK, "https://example.com/path/to/page?param=value&size=large"),
            TextNode(" here", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_links_with_special_chars(self):
        node = TextNode("Link with [special & chars!](https://example.com?q=test&lang=en) text", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("Link with ", TextType.TEXT),
            TextNode("special & chars!", TextType.LINK, "https://example.com?q=test&lang=en"),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_links_non_text_nodes_unchanged(self):
        nodes = [
            TextNode("Text with [link](https://example.com)", TextType.TEXT),
            TextNode("Bold text", TextType.BOLD),
            TextNode("Code text", TextType.CODE),
        ]
        new_nodes = split_nodes_link(nodes)
        expected = [
            TextNode("Text with ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://example.com"),
            TextNode("Bold text", TextType.BOLD),
            TextNode("Code text", TextType.CODE),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_links_mixed_with_existing_link_nodes(self):
        nodes = [
            TextNode("Text with [new link](https://example.com/new)", TextType.TEXT),
            TextNode("existing link", TextType.LINK, "https://example.com/existing"),
        ]
        new_nodes = split_nodes_link(nodes)
        expected = [
            TextNode("Text with ", TextType.TEXT),
            TextNode("new link", TextType.LINK, "https://example.com/new"),
            TextNode("existing link", TextType.LINK, "https://example.com/existing"),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_links_ignores_images(self):
        node = TextNode("Text with ![image](https://example.com/img.png) and [link](https://example.com)", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("Text with ![image](https://example.com/img.png) and ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://example.com"),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_links_with_nested_brackets_in_text(self):
        node = TextNode("Link with [text with [nested] brackets](https://example.com) here", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("Link with [text with [nested] brackets](https://example.com) here", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_links_mixed_with_images_comprehensive(self):
        node = TextNode("Start ![img](https://img.com) then [link](https://link.com) end", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("Start ![img](https://img.com) then ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://link.com"),
            TextNode(" end", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)


class TestTextToTextnodes(unittest.TestCase):
    def test_text_to_textnodes_comprehensive(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.TEXT),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]
        self.assertEqual(nodes, expected)

    def test_text_to_textnodes_plain_text(self):
        text = "This is just plain text with no markdown"
        nodes = text_to_textnodes(text)
        expected = [TextNode("This is just plain text with no markdown", TextType.TEXT)]
        self.assertEqual(nodes, expected)

    def test_text_to_textnodes_only_bold(self):
        text = "This is **bold** text"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertEqual(nodes, expected)

    def test_text_to_textnodes_only_italic(self):
        text = "This is *italic* text"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertEqual(nodes, expected)

    def test_text_to_textnodes_only_code(self):
        text = "This is `code` text"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertEqual(nodes, expected)

    def test_text_to_textnodes_only_image(self):
        text = "This has an ![image](https://example.com/img.png)"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This has an ", TextType.TEXT),
            TextNode("image", TextType.IMAGE, "https://example.com/img.png"),
        ]
        self.assertEqual(nodes, expected)

    def test_text_to_textnodes_only_link(self):
        text = "This has a [link](https://example.com)"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This has a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://example.com"),
        ]
        self.assertEqual(nodes, expected)

    def test_text_to_textnodes_multiple_same_type(self):
        text = "Multiple **bold** and **more bold** text"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("Multiple ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" and ", TextType.TEXT),
            TextNode("more bold", TextType.BOLD),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertEqual(nodes, expected)

    def test_text_to_textnodes_nested_emphasis(self):
        text = "Text with **bold *and italic* together** here"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("Text with ", TextType.TEXT),
            TextNode("bold *and italic* together", TextType.BOLD),
            TextNode(" here", TextType.TEXT),
        ]
        self.assertEqual(nodes, expected)

    def test_text_to_textnodes_consecutive_formatting(self):
        text = "**bold**_italic_`code`"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("bold", TextType.BOLD),
            TextNode("italic", TextType.ITALIC),
            TextNode("code", TextType.CODE),
        ]
        self.assertEqual(nodes, expected)

    def test_text_to_textnodes_empty_formatting(self):
        text = "Text with **bold** and ** ** empty bold"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("Text with ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" and ", TextType.TEXT),
            TextNode(" ", TextType.BOLD),
            TextNode(" empty bold", TextType.TEXT),
        ]
        self.assertEqual(nodes, expected)

    def test_text_to_textnodes_complex_mixed(self):
        text = "Start **bold** then *italic* with `code` and ![img](https://img.com) plus [link](https://link.com) end"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("Start ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" then ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" with ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" and ", TextType.TEXT),
            TextNode("img", TextType.IMAGE, "https://img.com"),
            TextNode(" plus ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://link.com"),
            TextNode(" end", TextType.TEXT),
        ]
        self.assertEqual(nodes, expected)

    def test_text_to_textnodes_bold_at_start_end(self):
        text = "**bold start** middle **bold end**"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("bold start", TextType.BOLD),
            TextNode(" middle ", TextType.TEXT),
            TextNode("bold end", TextType.BOLD),
        ]
        self.assertEqual(nodes, expected)

    def test_text_to_textnodes_asterisk_vs_bold(self):
        text = "Single *italic* and double **bold** asterisks"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("Single ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" and double ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" asterisks", TextType.TEXT),
        ]
        self.assertEqual(nodes, expected)

    def test_text_to_textnodes_image_and_link_together(self):
        text = "Check ![image](https://img.com) and [link](https://link.com) together"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("Check ", TextType.TEXT),
            TextNode("image", TextType.IMAGE, "https://img.com"),
            TextNode(" and ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://link.com"),
            TextNode(" together", TextType.TEXT),
        ]
        self.assertEqual(nodes, expected)

    def test_text_to_textnodes_all_types_sequential(self):
        text = "**bold** *italic* `code` ![image](https://img.com) [link](https://link.com)"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("bold", TextType.BOLD),
            TextNode(" ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" ", TextType.TEXT),
            TextNode("image", TextType.IMAGE, "https://img.com"),
            TextNode(" ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://link.com"),
        ]
        self.assertEqual(nodes, expected)

    def test_text_to_textnodes_empty_string(self):
        text = ""
        nodes = text_to_textnodes(text)
        expected = []
        self.assertEqual(nodes, expected)

    def test_text_to_textnodes_whitespace_only(self):
        text = "   "
        nodes = text_to_textnodes(text)
        expected = [TextNode("   ", TextType.TEXT)]
        self.assertEqual(nodes, expected)

    def test_text_to_textnodes_special_chars_in_text(self):
        text = "Text with **special & chars!** and *symbols @#$%* here"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("Text with ", TextType.TEXT),
            TextNode("special & chars!", TextType.BOLD),
            TextNode(" and ", TextType.TEXT),
            TextNode("symbols @#$%", TextType.ITALIC),
            TextNode(" here", TextType.TEXT),
        ]
        self.assertEqual(nodes, expected)


class TestMarkdownToBlocks(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_markdown_to_blocks_excessive_whitespace(self):
        md = """


This is a paragraph


Another paragraph




Final paragraph



"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is a paragraph",
                "Another paragraph",
                "Final paragraph",
            ],
        )

    def test_markdown_to_blocks_single_block(self):
        md = "Just one paragraph"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["Just one paragraph"])

    def test_markdown_to_blocks_empty_string(self):
        md = ""
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [])

    def test_markdown_to_blocks_only_whitespace(self):
        md = "   \n\n   \n\n   "
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [])

    def test_markdown_to_blocks_with_tabs(self):
        md = "\t\tTabbed paragraph\n\n\t\tAnother tabbed paragraph"
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "Tabbed paragraph",
                "Another tabbed paragraph",
            ],
        )


class TestBlockToBlockType(unittest.TestCase):
    def test_heading_h1(self):
        block = "# This is a heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)

    def test_heading_h2(self):
        block = "## This is a heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)

    def test_heading_h3(self):
        block = "### This is a heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)

    def test_heading_h4(self):
        block = "#### This is a heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)

    def test_heading_h5(self):
        block = "##### This is a heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)

    def test_heading_h6(self):
        block = "###### This is a heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)

    def test_heading_no_space_after_hash(self):
        block = "#This is not a heading"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_heading_too_many_hashes(self):
        block = "####### This is not a heading"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_code_block(self):
        block = "```\nprint('hello world')\n```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)

    def test_code_block_with_language(self):
        block = "```python\nprint('hello world')\n```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)

    def test_code_block_multiline(self):
        block = "```\nprint('hello')\nprint('world')\n```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)

    def test_code_block_incomplete_start(self):
        block = "``\nprint('hello world')\n```"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_code_block_incomplete_end(self):
        block = "```\nprint('hello world')\n``"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_code_block_too_short(self):
        block = "```"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_quote_single_line(self):
        block = "> This is a quote"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_quote_multiline(self):
        block = "> This is a quote\n> with multiple lines"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_quote_complex(self):
        block = "> This is the first line\n> This is the second line\n> This is the third line"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_quote_missing_space(self):
        block = ">This is not a quote"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_quote_inconsistent(self):
        block = "> This starts as a quote\nBut this line doesn't"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_unordered_list_single_item(self):
        block = "- This is a list item"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)

    def test_unordered_list_multiple_items(self):
        block = "- First item\n- Second item\n- Third item"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)

    def test_unordered_list_missing_space(self):
        block = "-This is not a list item"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_unordered_list_inconsistent(self):
        block = "- This is a list item\nThis is not"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_ordered_list_single_item(self):
        block = "1. This is an ordered list item"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

    def test_ordered_list_multiple_items(self):
        block = "1. First item\n2. Second item\n3. Third item"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

    def test_ordered_list_wrong_starting_number(self):
        block = "2. This doesn't start with 1"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_ordered_list_non_sequential(self):
        block = "1. First item\n3. Third item"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_ordered_list_missing_space(self):
        block = "1.This is not a list item"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_ordered_list_missing_period(self):
        block = "1 This is not a list item"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_ordered_list_inconsistent(self):
        block = "1. This is a list item\nThis is not"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_paragraph_plain_text(self):
        block = "This is just a regular paragraph"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_paragraph_multiline(self):
        block = "This is a paragraph\nwith multiple lines"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_paragraph_with_markdown(self):
        block = "This is a **bold** paragraph with *italic* text"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_paragraph_empty_string(self):
        block = ""
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_paragraph_hash_without_space(self):
        block = "#notaheading"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_paragraph_with_backticks_not_code(self):
        block = "This has `inline code` but is not a code block"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_paragraph_with_greater_than(self):
        block = "This text has > symbols but is not a quote"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_paragraph_with_dash(self):
        block = "This text has - symbols but is not a list"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_paragraph_with_numbers(self):
        block = "This text has 1. numbers but is not a list"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)


class TestMarkdownToHtmlNode(unittest.TestCase):
    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    def test_heading(self):
        md = """
# This is an H1

## This is an H2

### This is an H3
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h1>This is an H1</h1><h2>This is an H2</h2><h3>This is an H3</h3></div>",
        )

    def test_quote(self):
        md = """
> This is a quote
> with multiple lines
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><blockquote>This is a quote\nwith multiple lines</blockquote></div>",
        )

    def test_unordered_list(self):
        md = """
- First item
- Second item
- Third item
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ul><li>First item</li><li>Second item</li><li>Third item</li></ul></div>",
        )

    def test_ordered_list(self):
        md = """
1. First item
2. Second item
3. Third item
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ol><li>First item</li><li>Second item</li><li>Third item</li></ol></div>",
        )

    def test_mixed_content(self):
        md = """
# Heading

This is a **bold** paragraph.

- List item 1
- List item 2

> This is a quote

```
code block
```
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        expected = "<div><h1>Heading</h1><p>This is a <b>bold</b> paragraph.</p><ul><li>List item 1</li><li>List item 2</li></ul><blockquote>This is a quote</blockquote><pre><code>code block\n</code></pre></div>"
        self.assertEqual(html, expected)

    def test_paragraph_with_inline_formatting(self):
        md = """
This paragraph has **bold**, *italic*, `code`, [link](https://example.com), and ![image](https://example.com/img.png) elements.
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        expected = '<div><p>This paragraph has <b>bold</b>, <i>italic</i>, <code>code</code>, <a href="https://example.com">link</a>, and <img src="https://example.com/img.png" alt="image"> elements.</p></div>'
        self.assertEqual(html, expected)

    def test_empty_markdown(self):
        md = ""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div></div>")

    def test_heading_with_formatting(self):
        md = """
# This is a **bold** heading
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h1>This is a <b>bold</b> heading</h1></div>",
        )


if __name__ == "__main__":
    unittest.main()
