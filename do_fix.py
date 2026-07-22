# Fix corrupted theme.py
filepath = r'c:/Users/suraj/OneDrive/Desktop/db/Data Science Course/Vocational Training project/ai_resume_analyzer/utils/theme.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# The corrupted section: the render_page_header function def line is missing,
# leaving orphan body code starting with "            {eyebrow_html}"
# We need to:
# 1. Find the orphan body
# 2. Replace it with the proper function definition + page_header alias

orphan_start = content.find('            {eyebrow_html}')
orphan_end = content.find('def render_section_header', orphan_start)

if orphan_start == -1 or orphan_end == -1:
    print("ERROR: Could not find corrupted section")
    exit(1)

orphan_block = content[orphan_start:orphan_end]
print(f"Found orphan block at pos {orphan_start} to {orphan_end}")
print(f"Length: {orphan_end - orphan_start}")

# The replacement: render_page_header function + page_header alias
replacement = """def render_page_header(title, description="", icon="", eyebrow=None):
    \"\"\"Render a premium page header.\"\"\"
    safe_title = escape_html(title)
    safe_description = escape_html(description)
    safe_icon = f"{escape_html(icon)} " if icon else ""
    eyebrow_html = (
        f'<div class="eyebrow">{escape_html(eyebrow)}</div>' if eyebrow else ""
    )

    st.html(f"""
        <div class="saas-page-header">
            {eyebrow_html}
            <h1>{safe_icon}{safe_title}</h1>
            {"<p>" + safe_description + "</p>" if safe_description else ""}
        </div>
        """)


def page_header(title, description="", icon="", eyebrow=None):
    \"\"\"Backward-compatible alias that also supports the eyebrow parameter.\"\"\"
    render_page_header(title, description, icon, eyebrow=eyebrow)

"""

new_content = content[:orphan_start] + replacement + content[orphan_end:]

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Successfully fixed theme.py!")

# Verify
with open(filepath, 'r', encoding='utf-8') as f:
    verify = f.read()

print(f"render_page_header present: {'def render_page_header' in verify}")
print(f"page_header present: {'def page_header' in verify}")
print(f"render_section_header present: {'def render_section_header' in verify}")
</｜｜DSML｜｜parameter>
</create_file>
