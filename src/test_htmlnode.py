
import unittest
from src.htmlnode import HTMLNode, LeafNode, ParentNode


class TestHTMLNode(unittest.TestCase):
    def test_to_html_props(self):
        node = HTMLNode(
            "div",
            "Hello, world!",
            None,
            {"class": "greeting", "href": "https://boot.dev"},
        )
        self.assertEqual(
            node.props_to_html(),
            ' class="greeting" href="https://boot.dev"',
        )

    def test_values(self):
        node = HTMLNode(
            "div",
            "I wish I could read",
        )
        self.assertEqual(
            node.tag,
            "div",
        )
        self.assertEqual(
            node.value,
            "I wish I could read",
        )
        self.assertEqual(
            node.children,
            None,
        )
        self.assertEqual(
            node.props,
            None,
        )

    def test_repr(self):
        # Placeholder for repr test
        self.assertIsInstance(repr(HTMLNode("div", "test")), str)


class TestLeafNode(unittest.TestCase):
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_tagless(self):
        node = LeafNode(None, "Just text")
        self.assertEqual(node.to_html(), "Just text")

    def test_leaf_to_html_with_props(self):
        node = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
        self.assertEqual(node.to_html(), '<a href="https://www.google.com">Click me!</a>')

    def test_leaf_to_html_raises_without_value(self):
        with self.assertRaises(ValueError):
            LeafNode("p", None).to_html()
        pass


class TestParentNode(unittest.TestCase):
    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_to_html_multiple_children(self):
        child1 = LeafNode("span", "child1")
        child2 = LeafNode("p", "child2")
        child3 = LeafNode(None, "plain text")
        parent_node = ParentNode("div", [child1, child2, child3])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span>child1</span><p>child2</p>plain text</div>"
        )

    def test_to_html_nested_parent_nodes(self):
        leaf1 = LeafNode("b", "Bold")
        leaf2 = LeafNode("i", "Italic")
        parent1 = ParentNode("p", [leaf1])
        parent2 = ParentNode("p", [leaf2])
        root_parent = ParentNode("div", [parent1, parent2])
        self.assertEqual(
            root_parent.to_html(),
            "<div><p><b>Bold</b></p><p><i>Italic</i></p></div>"
        )

    def test_to_html_with_props(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node], {"class": "container", "id": "main"})
        self.assertEqual(
            parent_node.to_html(),
            '<div class="container" id="main"><span>child</span></div>'
        )

    def test_to_html_children_with_props(self):
        child1 = LeafNode("a", "Link", {"href": "http://example.com"})
        child2 = LeafNode("span", "Text", {"class": "highlight"})
        parent_node = ParentNode("div", [child1, child2])
        self.assertEqual(
            parent_node.to_html(),
            '<div><a href="http://example.com">Link</a><span class="highlight">Text</span></div>'
        )

    def test_to_html_deep_nesting(self):
        innermost = LeafNode("strong", "Deep text")
        level3 = ParentNode("em", [innermost])
        level2 = ParentNode("span", [level3])
        level1 = ParentNode("p", [level2])
        root = ParentNode("div", [level1])
        self.assertEqual(
            root.to_html(),
            "<div><p><span><em><strong>Deep text</strong></em></span></p></div>"
        )

    def test_to_html_mixed_children_types(self):
        leaf1 = LeafNode("b", "Bold")
        leaf2 = LeafNode(None, " and ")
        inner_parent = ParentNode("i", [LeafNode(None, "italic")])
        leaf3 = LeafNode(None, " text")
        parent_node = ParentNode("p", [leaf1, leaf2, inner_parent, leaf3])
        self.assertEqual(
            parent_node.to_html(),
            "<p><b>Bold</b> and <i>italic</i> text</p>"
        )

    def test_to_html_empty_children_list(self):
        parent_node = ParentNode("div", [])
        self.assertEqual(parent_node.to_html(), "<div></div>")

    def test_to_html_no_tag_raises_error(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode(None, [child_node])
        with self.assertRaises(ValueError) as context:
            parent_node.to_html()
        self.assertIn("no tag", str(context.exception))

    def test_to_html_no_children_raises_error(self):
        parent_node = ParentNode("div", None)
        with self.assertRaises(ValueError) as context:
            parent_node.to_html()
        self.assertIn("no children", str(context.exception))

    def test_complex_example(self):
        # The example from the user's question
        node = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, "Normal text"),
                LeafNode("i", "italic text"),
                LeafNode(None, "Normal text"),
            ],
        )
        self.assertEqual(
            node.to_html(),
            "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>"
        )

    def test_repr(self):
        child = LeafNode("span", "test")
        parent = ParentNode("div", [child])
        repr_str = repr(parent)
        self.assertIn("ParentNode", repr_str)
        self.assertIn("div", repr_str)


