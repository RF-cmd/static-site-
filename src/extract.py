import os
from markdown_blocks import markdown_to_html_node


def generate_page(from_path, template_path, dest_path):
    print(f" * {from_path} {template_path} -> {dest_path}")
    from_file = open(from_path, "r")
    markdown_content = from_file.read()
    from_file.close()

    template_file = open(template_path, "r")
    template = template_file.read()
    template_file.close()

    node = markdown_to_html_node(markdown_content)
    html = node.to_html()

    title = extract_title(markdown_content)
    template = template.replace("{{ Title }}", title)
    template = template.replace("{{ Content }}", html)

    dest_dir_path = os.path.dirname(dest_path)
    if dest_dir_path != "":
        os.makedirs(dest_dir_path, exist_ok=True)
    to_file = open(dest_path, "w")
    to_file.write(template)


def generate_pages_recursive(dir_path_content, template_path, dest_dir_path):
    # Walk through the content directory
    for root, dirs, files in os.walk(dir_path_content):
        for file in files:
            if file.endswith(".md"):  # Check if the file is a markdown file
                # Full path of the markdown file
                from_path = os.path.join(root, file)

                # Calculate the relative path of the markdown file within the content directory
                relative_path = os.path.relpath(from_path, dir_path_content)

                # Replace .md extension with .html and construct the destination path
                dest_path = os.path.join(dest_dir_path, os.path.splitext(relative_path)[0] + ".html")

                # Call the generate_page function to generate the HTML file
                generate_page(from_path, template_path, dest_path)

    # Special handling for a specific page if needed
    # For example, serve the contents.html directly at /majesty
    specific_page_src = os.path.join(dir_path_content, "contents.md")
    specific_page_dest = os.path.join(dest_dir_path, "contents.html")
    if os.path.exists(specific_page_src):
        generate_page(specific_page_src, template_path, specific_page_dest)


def extract_title(md):
    lines = md.split("\n")
    for line in lines:
        if line.startswith("# "):
            return line[2:]
    raise ValueError("No title found")
