import unittest

from textnode import TextNode, TextType, split_nodes_delimiter


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


if __name__ == "__main__":
    unittest.main()
