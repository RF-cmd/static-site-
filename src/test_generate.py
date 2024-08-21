import unittest
import os
from extract import generate_page, extract_title

class TestGeneratePageSimple(unittest.TestCase):

    def setUp(self):
        # Setup paths for testing
        self.markdown_content = "# tolkien func club "
        self.template_content = "<html><head><title>{{ Title }}</title></head><body>{{ Content }}</body></html>"
        self.dest_path = "output/simple_test.html"
        self.markdown_path = "test_simple.md"
        self.template_path = "template_simple.html"

        # Write the markdown content to a file
        with open(self.markdown_path, 'w') as f:
            f.write(self.markdown_content)

        # Write the template content to a file
        with open(self.template_path, 'w') as f:
            f.write(self.template_content)

    def tearDown(self):
        # Clean up the files after test
        if os.path.exists(self.markdown_path):
            os.remove(self.markdown_path)
        if os.path.exists(self.template_path):
            os.remove(self.template_path)
        if os.path.exists(self.dest_path):
            os.remove(self.dest_path)

    def test_extract_title_simple(self):
        # Test extracting the title from markdown
        title = extract_title(self.markdown_content)
        #self.assertEqual(title, "Simple Title")

    def test_generate_page_simple(self):
        # Test generating a page from simple markdown
        generate_page(self.markdown_path, self.template_path, self.dest_path)

        # Check that the destination file was created
        self.assertTrue(os.path.exists(self.dest_path))

        # Read the generated file and check its contents
        with open(self.dest_path, 'r') as f:
            generated_content = f.read()

        # Check that the title and content are properly replaced
        self.assertIn("<title>Simple Title</title>", generated_content)
        self.assertIn("<body><p>This is a simple paragraph without links.</p></body>", generated_content)

if __name__ == "__main__":
    unittest.main()