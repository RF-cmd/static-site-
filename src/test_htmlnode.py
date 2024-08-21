from htmlnode import HTMLNode, LeafNode, ParentNode, TextNode, text_node_to_html_node, split_nodes_delimiter, \
    extract_markdown_images, extract_markdown_links, split_nodes_link, split_nodes_image
import unittest
import sys

# Update the path to where your HTMLNode class is located
sys.path.append('//wsl.localhost/Ubuntu/home/lazaros/server/public/src')


class TestHTMLNode(unittest.TestCase):

    def test_props_to_html(self):
        # Test case with no props
        node = HTMLNode(tag="div", props={})
        self.assertEqual(node.props_to_html(), "")

        # Test case with multiple props
        node = HTMLNode(tag="a", props={"href": "https://www.google.com", "target": "_blank"})
        self.assertEqual(node.props_to_html(), ' href="https://www.google.com" target="_blank"')

        # Test case with a single prop
        node = HTMLNode(tag="img", props={"src": "image.png"})
        self.assertEqual(node.props_to_html(), ' src="image.png"')

        # Test case with special characters in props
        node = HTMLNode(tag="input", props={"type": "text", "value": "O'Reilly & Co."})
        self.assertEqual(node.props_to_html(), ' type="text" value="O\'Reilly & Co."')

        # Test case with numeric props
        node = HTMLNode(tag="progress", props={"value": 50, "max": 100})
        self.assertEqual(node.props_to_html(), ' value="50" max="100"')

    def test_repr(self):
        # Test __repr__ method with no children and no props
        node = HTMLNode(tag="span", value="Hello World", children=[], props={})
        expected_repr = "<HTMLNode(tag='span', value='Hello World', children=0, props={})>"
        self.assertEqual(repr(node), expected_repr)

        # Test __repr__ method with children and props
        child_node = HTMLNode(tag="b", value="Bold text")
        node = HTMLNode(tag="div", value=None, children=[child_node], props={"class": "container"})
        expected_repr = "<HTMLNode(tag='div', value='None', children=1, props={'class': 'container'})>"
        self.assertEqual(repr(node), expected_repr)

    def test_node_with_children(self):
        # Test a node with multiple children
        child1 = HTMLNode(tag="li", value="Item 1")
        child2 = HTMLNode(tag="li", value="Item 2")
        parent = HTMLNode(tag="ul", children=[child1, child2])
        expected_repr = "<HTMLNode(tag='ul', value='None', children=2, props={})>"
        self.assertEqual(repr(parent), expected_repr)

        # Test a node with deeply nested children
        child = HTMLNode(tag="p", value="Deep child")
        middle_child = HTMLNode(tag="div", children=[child])
        root = HTMLNode(tag="section", children=[middle_child])
        expected_repr = "<HTMLNode(tag='section', value='None', children=1, props={})>"
        self.assertEqual(repr(root), expected_repr)
        self.assertEqual(repr(root.children[0]), "<HTMLNode(tag='div', value='None', children=1, props={})>")
        self.assertEqual(repr(root.children[0].children[0]),
                         "<HTMLNode(tag='p', value='Deep child', children=0, props={})>")

    def test_node_initialization(self):
        # Test default initialization of a node
        node = HTMLNode(tag="p")
        self.assertEqual(node.tag, "p")
        self.assertEqual(node.value, None)
        self.assertEqual(node.children, [])
        self.assertEqual(node.props, {})

        # Test initialization with all attributes provided
        node = HTMLNode(tag="a", value="Click here", children=[], props={"href": "https://example.com"})
        self.assertEqual(node.tag, "a")
        self.assertEqual(node.value, "Click here")
        self.assertEqual(node.children, [])
        self.assertEqual(node.props, {"href": "https://example.com"})

    def test_empty_strings(self):
        # Test node with empty value and props
        node = HTMLNode(tag="div", value="", props={"class": ""})
        self.assertEqual(node.value, "")
        self.assertEqual(node.props_to_html(), ' class=""')
        expected_repr = "<HTMLNode(tag='div', value='', children=0, props={'class': ''})>"
        self.assertEqual(repr(node), expected_repr)

    def test_special_cases(self):
        # Test node with props having None values (should be excluded from props_to_html)
        node = HTMLNode(tag="input", props={"type": "text", "placeholder": None})
        self.assertEqual(node.props_to_html(), ' type="text"')

        # Test node with empty props dictionary
        node = HTMLNode(tag="img", props={})
        self.assertEqual(node.props_to_html(), "")

        # Test node with large number of children
        children = [HTMLNode(tag="li", value=f"Item {i}") for i in range(100)]
        parent = HTMLNode(tag="ul", children=children)
        self.assertEqual(len(parent.children), 100)
        self.assertEqual(repr(parent), "<HTMLNode(tag='ul', value='None', children=100, props={})>")

    def test_leaf_node_creation(self):
        # Test creating a valid LeafNode
        node = LeafNode("p", "Hello")
        self.assertEqual(node.tag, "p")
        self.assertEqual(node.value, "Hello")
        self.assertEqual(node.children, [])  # No children allowed
        self.assertEqual(node.props, {})

    def test_leaf_node_no_value(self):
        # Test creating a LeafNode without a value (should raise an error)
        with self.assertRaises(ValueError):
            LeafNode("p", None)

    def test_leaf_node_to_html(self):
        # Test rendering a LeafNode as HTML
        node = LeafNode("p", "This is a paragraph.")
        self.assertEqual(node.to_html(), "<p>This is a paragraph.</p>")

        node_with_props = LeafNode("a", "Click here!", {"href": "https://example.com"})
        self.assertEqual(node_with_props.to_html(), '<a href="https://example.com">Click here!</a>')

    def test_leaf_node_raw_text(self):
        # Test rendering a LeafNode with no tag (should return raw value)
        node = LeafNode(None, "Raw text")
        self.assertEqual(node.to_html(), "Raw text")

    def test_parent_node_creation(self):
        # Test creating a valid ParentNode
        child1 = LeafNode("b", "Bold text")
        child2 = LeafNode(None, "Normal text")
        node = ParentNode("p", [child1, child2])
        self.assertEqual(node.tag, "p")
        self.assertEqual(len(node.children), 2)
        self.assertEqual(node.value, None)

    def test_parent_node_no_tag(self):
        # Test creating a ParentNode without a tag (should raise an error)
        child = LeafNode("b", "Bold text")
        with self.assertRaises(ValueError):
            ParentNode(None, [child]).to_html()

    def test_parent_node_no_children(self):
        # Test creating a ParentNode without children (should raise an error)
        with self.assertRaises(ValueError):
            ParentNode("p", []).to_html()

    def test_parent_node_to_html(self):
        # Test rendering a ParentNode as HTML
        node = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, "Normal text"),
                LeafNode("i", "italic text"),
                LeafNode(None, "Normal text"),
            ],
        )
        self.assertEqual(node.to_html(), "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>")

    def test_parent_node_multiple_children(self):
        # Test a ParentNode with multiple children
        children = [LeafNode("span", f"Child {i}") for i in range(10)]
        node = ParentNode("div", children)
        expected_html = "<div>" + "".join([f"<span>Child {i}</span>" for i in range(10)]) + "</div>"
        self.assertEqual(node.to_html(), expected_html)

    def test_parent_node_deep_nesting(self):
        # Test a deeply nested ParentNode structure
        deep_node = LeafNode("span", "Deepest text")
        for _ in range(50):  # 50 levels deep
            deep_node = ParentNode("div", [deep_node])
        self.assertTrue(deep_node.to_html().startswith("<div>"))
        self.assertTrue(deep_node.to_html().endswith("Deepest text</span></div>" + "</div>" * 49))

    def test_parent_node_special_characters_in_tag(self):
        # Test ParentNode with a tag containing special characters
        with self.assertRaises(ValueError):
            ParentNode("div<script>", [LeafNode("b", "Text")]).to_html()

    def test_parent_node_large_number_of_children(self):
        # Test a ParentNode with a very large number of children
        children = [LeafNode("span", f"Child {i}") for i in range(300)]
        node = ParentNode("div", children)
        self.assertTrue(len(node.to_html()) > 300)  # Very large HTML output

    def test_parent_node_empty_children(self):
        # Test ParentNode with empty string children
        children = [LeafNode("span", "") for _ in range(5)]
        node = ParentNode("div", children)
        expected_html = "<div>" + "".join(["<span></span>"] * 5) + "</div>"
        self.assertEqual(node.to_html(), expected_html)

    def test_parent_node_mixed_tags_and_raw_text(self):
        # Test ParentNode with a mix of tags and raw text
        node = ParentNode(
            "div",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, " raw text "),
                LeafNode("i", "italic text"),
            ],
        )
        self.assertEqual(node.to_html(), "<div><b>Bold text</b> raw text <i>italic text</i></div>")

    def test_parent_node_with_empty_tag(self):
        # Test ParentNode with an empty string as a tag (should raise an error)
        with self.assertRaises(ValueError):
            ParentNode("", [LeafNode("b", "Bold text")]).to_html()

    def test_parent_node_with_space_in_tag(self):
        # Test ParentNode with a space in the tag (should raise an error)
        with self.assertRaises(ValueError):
            ParentNode("invalid tag", [LeafNode("b", "Text")]).to_html()

    def test_parent_node_only_whitespace_children(self):
        # Test ParentNode with children that are only whitespace
        children = [LeafNode("span", " "), LeafNode(None, "\t"), LeafNode("span", "\n")]
        node = ParentNode("div", children)
        expected_html = "<div><span> </span>\t<span>\n</span></div>"
        self.assertEqual(node.to_html(), expected_html)

    def test_parent_node_nested_with_no_children(self):
        # Test ParentNode nested within another with no children (should raise an error)
        child = ParentNode("span", [LeafNode("b", "Text")])
        with self.assertRaises(ValueError):
            ParentNode("div", [child, ParentNode("p", [])]).to_html()

    def test_parent_node_tag_with_numbers(self):
        # Test ParentNode with a numeric tag (which is invalid, should raise an error)
        with self.assertRaises(ValueError):
            ParentNode("123tag", [LeafNode("b", "Text")]).to_html()

    def test_parent_node_children_with_tags_as_none(self):
        # Test ParentNode with children having None as a tag
        children = [LeafNode(None, "Text 1"), LeafNode(None, "Text 2")]
        node = ParentNode("div", children)
        self.assertEqual(node.to_html(), "<div>Text 1Text 2</div>")

    def test_parent_node_html_entity_in_value(self):
        # Test handling of HTML entities in the value
        child = LeafNode("p", "&lt; &gt; &amp;")
        node = ParentNode("div", [child])
        self.assertEqual(node.to_html(), "<div><p>&lt; &gt; &amp;</p></div>")

    def test_parent_node_tag_case_sensitivity(self):
        # Test ParentNode with uppercase tag
        node = ParentNode("DIV", [LeafNode("P", "Text")])
        self.assertEqual(node.to_html(), "<DIV><P>Text</P></DIV>")

    def test_parent_node_unusual_whitespace_in_value(self):
        # Test LeafNode values with unusual whitespace
        child = LeafNode("p", "Text\nwith\nnewlines")
        node = ParentNode("div", [child])
        self.assertEqual(node.to_html(), "<div><p>Text\nwith\nnewlines</p></div>")

    def test_parent_node_with_unusual_props(self):
        # Test ParentNode with unusual props
        node = ParentNode("div", [LeafNode("p", "Text", {"data-attr": "value", "id": "unique"})])
        self.assertEqual(node.to_html(), '<div><p data-attr="value" id="unique">Text</p></div>')

    def test_parent_node_with_empty_string_tag(self):
        # Test ParentNode with an empty string tag (should raise an error)
        with self.assertRaises(ValueError):
            ParentNode("", [LeafNode("p", "Text")]).to_html()

    def test_parent_node_with_multiline_text(self):
        # Test ParentNode with multiline text in children
        child = LeafNode("p", "Line 1\nLine 2\nLine 3")
        node = ParentNode("div", [child])
        self.assertEqual(node.to_html(), "<div><p>Line 1\nLine 2\nLine 3</p></div>")
    def test_text_type_text(self):
        text_node = TextNode("text", "This is some text")
        html_node = text_node_to_html_node(text_node)
        self.assertIsInstance(html_node, LeafNode)
        self.assertEqual(html_node.to_html(), "This is some text")

    def test_text_type_bold(self):
        bold_node = TextNode("bold", "Bold text")
        html_node = text_node_to_html_node(bold_node)
        self.assertIsInstance(html_node, LeafNode)
        self.assertEqual(html_node.to_html(), "<b>Bold text</b>")

    def test_text_type_italic(self):
        italic_node = TextNode("italic", "Italic text")
        html_node = text_node_to_html_node(italic_node)
        self.assertIsInstance(html_node, LeafNode)
        self.assertEqual(html_node.to_html(), "<i>Italic text</i>")

    def test_text_type_code(self):
        code_node = TextNode("code", "print('Hello, World!')")
        html_node = text_node_to_html_node(code_node)
        self.assertIsInstance(html_node, LeafNode)
        self.assertEqual(html_node.to_html(), "<code>print('Hello, World!')</code>")

    def test_text_type_link(self):
        link_node = TextNode("link", "Click here", href="https://example.com")
        html_node = text_node_to_html_node(link_node)
        self.assertIsInstance(html_node, LeafNode)
        self.assertEqual(html_node.to_html(), '<a href="https://example.com">Click here</a>')

    def test_text_type_link_missing_href(self):
        with self.assertRaises(ValueError):
            link_node = TextNode("link", "Click here")
            text_node_to_html_node(link_node)

    def test_text_type_image(self):
        image_node = TextNode("image", "", src="https://example.com/image.jpg", alt="Example Image")
        html_node = text_node_to_html_node(image_node)
        self.assertIsInstance(html_node, LeafNode)
        self.assertEqual(html_node.to_html(), '<img src="https://example.com/image.jpg" alt="Example Image"></img>')

    def test_text_type_image_missing_src(self):
        with self.assertRaises(ValueError):
            image_node = TextNode("image", "")
            text_node_to_html_node(image_node)

    def test_unknown_text_type(self):
        with self.assertRaises(ValueError):
            unknown_node = TextNode("unknown", "Unknown text type")
            text_node_to_html_node(unknown_node)

    def test_invalid_text_node(self):
        with self.assertRaises(TypeError):
            text_node_to_html_node("This is not a TextNode")


    def test_no_delimiter_exception(self):
        node = TextNode("text", "This is text with no delimiters here.")
        with self.assertRaises(ValueError) as context:
            split_nodes_delimiter([node], "*", "italic")
        # self.assertIn("No delimiter", str(context.exception))
        # self.assertIn("This is text", str(context.exception))  # Ensure the first few words are included

    def test_basic_text_with_single_delimiter(self):
        node = TextNode("text", "This is text with a `code block` word")
        result = split_nodes_delimiter([node], "`", "code")
        # self.assertEqual(len(result), 3)
        # self.assertEqual(result[0].content, "This is text with a ")
        # self.assertEqual(result[0].text_type, "text")
        # self.assertEqual(result[1].content, "code block")
        # self.assertEqual(result[1].text_type, "code")
        # self.assertEqual(result[2].content, " word")
        # self.assertEqual(result[2].text_type, "text")

    def test_text_with_multiple_delimiters(self):
        node = TextNode("text", "This is *italic* and **bold** text")
        result = split_nodes_delimiter([node], "*", "italic")
        result = split_nodes_delimiter(result, "**", "bold")
        # self.assertEqual(len(result), 5)
        # self.assertEqual(result[0].content, "This is ")
        # self.assertEqual(result[1].content, "italic")
        # self.assertEqual(result[1].text_type, "italic")
        # self.assertEqual(result[2].content, " and ")
        # self.assertEqual(result[3].content, "bold")
        # self.assertEqual(result[3].text_type, "bold")
        # self.assertEqual(result[4].content, " text")

    def test_text_with_nested_delimiters(self):
        node = TextNode("text", "This is **bold and *italic* inside**")
        result = split_nodes_delimiter([node], "*", "italic")
        result = split_nodes_delimiter(result, "**", "bold")
        # self.assertEqual(len(result), 3)
        # self.assertEqual(result[0].content, "This is ")
        # self.assertEqual(result[1].content, "bold and ")
        # self.assertEqual(result[1].text_type, "bold")
        # self.assertEqual(result[2].content, "italic")
        # self.assertEqual(result[2].text_type, "italic")

    def test_no_delimiters_present(self):
        node = TextNode("text", "This is plain text with no delimiters")
        with self.assertRaises(ValueError) as context:
            split_nodes_delimiter([node], "*", "italic")
        #self.assertIn("No delimiter", str(context.exception))

    def test_missing_closing_delimiter(self):
        node = TextNode("text", "This is text with an *italic start but no end")
        with self.assertRaises(ValueError) as context:
            split_nodes_delimiter([node], "*", "italic")
        #self.assertIn("Unmatched delimiter", str(context.exception))

    def test_extract_markdown_images_single(self):
        text = "This is a text with an image ![sample image](https://example.com/image.png)"
        expected = [("sample image", "https://example.com/image.png")]
        self.assertEqual(extract_markdown_images(text), expected)

    def test_extract_markdown_images_multiple(self):
        text = "Images: ![one](https://example.com/one.png) and ![two](https://example.com/two.png)"
        expected = [("one", "https://example.com/one.png"), ("two", "https://example.com/two.png")]
        self.assertEqual(extract_markdown_images(text), expected)

    def test_extract_markdown_images_none(self):
        text = "No images here."
        expected = []
        self.assertEqual(extract_markdown_images(text), expected)

    def test_extract_markdown_links_single(self):
        text = "This is a text with a link [example](https://example.com)"
        expected = [("example", "https://example.com")]
        self.assertEqual(extract_markdown_links(text), expected)

    def test_extract_markdown_links_multiple(self):
        text = "Links: [first](https://example.com/1) and [second](https://example.com/2)"
        expected = [("first", "https://example.com/1"), ("second", "https://example.com/2")]
        self.assertEqual(extract_markdown_links(text), expected)

    def test_split_nodes_link_basic(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev)",
            "text"
        )
        new_nodes = split_nodes_link([node])
        for n in new_nodes:
            print(f"TextNode({n.content!r}, {n.text_type!r}, {n.href!r})")

    def test_split_nodes_link_multiple(self):
        node = TextNode(
            "Link to [Google](https://www.google.com) and [YouTube](https://www.youtube.com)",
            "text"
        )
        new_nodes = split_nodes_link([node])
        for n in new_nodes:
            print(f"TextNode({n.content!r}, {n.text_type!r}, {n.href!r})")

    def test_split_nodes_link_no_links(self):
        node = TextNode(
            "This is just plain text with no links.",
            "text"
        )
        new_nodes = split_nodes_link([node])
        for n in new_nodes:
            print(f"TextNode({n.content!r}, {n.text_type!r}, {n.href!r})")

    def test_split_nodes_link_edge_case(self):
        node = TextNode(
            "[Empty](https://example.com) and [Valid](https://valid.com)",
            "text"
        )
        new_nodes = split_nodes_link([node])
        for n in new_nodes:
            print(f"TextNode({n.content!r}, {n.text_type!r}, {n.href!r})")

    def test_split_nodes_image_basic(self):
        node = TextNode(
            "Here is an image ![Alt Text](https://www.example.com/image.png)",
            "text"
        )
        new_nodes = split_nodes_image([node])
        for n in new_nodes:
            print(f"TextNode({n.content!r}, {n.text_type!r}, {n.href!r}, {n.src!r}, {n.alt!r})")

    def test_split_nodes_image_multiple(self):
        node = TextNode(
            "Images ![First](https://www.example.com/first.png) and ![Second](https://www.example.com/second.png)",
            "text"
        )
        new_nodes = split_nodes_image([node])
        for n in new_nodes:
            print(f"TextNode({n.content!r}, {n.text_type!r}, {n.href!r}, {n.src!r}, {n.alt!r})")

    def test_split_nodes_image_no_images(self):
        node = TextNode(
            "This is just plain text with no images.",
            "text"
        )
        new_nodes = split_nodes_image([node])
        for n in new_nodes:
            print(f"TextNode({n.content!r}, {n.text_type!r}, {n.href!r}, {n.src!r}, {n.alt!r})")

    def test_split_nodes_image_edge_case(self):
        node = TextNode(
            "![Alt](https://example.com/image.png) and ![Another](https://example.com/another.png)",
            "text"
        )
        new_nodes = split_nodes_image([node])
        for n in new_nodes:
            print(f"TextNode({n.content!r}, {n.text_type!r}, {n.href!r}, {n.src!r}, {n.alt!r})")

if __name__ == '__main__':
    unittest.main()