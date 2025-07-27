import subprocess
import tempfile
import os
import tiktoken
import re

def chunk_text(text, chunk_size=200, overlap=100, model="text-embedding-3-small"):
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)

    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunk_tokens = tokens[start:end]
        chunks.append(encoding.decode(chunk_tokens))
        start += chunk_size - overlap
    return chunks

def latex_to_markdown(latex_content: str) -> str:
    # Create a temporary .tex file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".tex", mode="w") as tmp_tex:
        tmp_tex.write(latex_content)
        tmp_tex_path = tmp_tex.name

    # Create a temporary .md file
    tmp_md_path = tmp_tex_path.replace(".tex", ".md")

    try:
        # Run pandoc to convert latex → markdown
        subprocess.run(
            ["pandoc", tmp_tex_path, "-f", "latex", "-t", "markdown", "-o", tmp_md_path],
            check=True,
        )
        # Read the markdown result
        with open(tmp_md_path, "r") as f:
            markdown_content = f.read()

        # Remove pandoc fenced divs like ::::: and :::
        markdown_content = re.sub(r':{2,}', '', markdown_content)
    finally:
        # Clean up temp files
        os.remove(tmp_tex_path)
        if os.path.exists(tmp_md_path):
            os.remove(tmp_md_path)

    return markdown_content