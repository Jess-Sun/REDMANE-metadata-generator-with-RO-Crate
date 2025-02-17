import json

def generate_html_from_json(json_path, html_path):
    """
    Dummy implementation that creates a simple HTML file from JSON.
    """
    with open(json_path, "r") as f:
        data = json.load(f)
    html_content = "<html><body><pre>" + json.dumps(data, indent=4) + "</pre></body></html>"
    with open(html_path, "w") as f:
        f.write(html_content)
    print(f"HTML report generated at: {html_path}")