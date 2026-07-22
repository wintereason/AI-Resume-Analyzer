import re

filepath = r'c:/Users/suraj/OneDrive/Desktop/db/Data Science Course/Vocational Training project/ai_resume_analyzer/utils/theme.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the orphan block starting with '{eyebrow_html}'
orphan_start = content.find('            {eyebrow_html}')
orphan_end = content.find('def render_section_header', orphan_start)

print("Orphan start:", orphan_start)
print("Orphan end:", orphan_end)

if orphan_start == -1 or orphan_end == -1:
    print("ERROR: Could not find corrupted section")
    exit(1)

# Replacement - render_page_header function with page_header alias
replacement_text = (
    'def render_page_header(title, description="", icon="", eyebrow=None):\n'
    '    """Render a premium page header."""\n'
    '    safe_title = escape_html(title)\n'
    '    safe_description = escape_html(description)\n'
    '    safe_icon = f"{escape_html(icon)} " if icon else ""\n'
    '    eyebrow_html = (\n'
    "        f'<div class=\"eyebrow\">{escape_html(eyebrow)}</div>' if eyebrow else \"\"\n"
    '    )\n'
    '\n'
    '    st.html(f"""\n'
    '        <div class="saas-page-header">\n'
    '            {eyebrow_html}\n'
    '            <h1>{safe_icon}{safe_title}</h1>\n'
    '            {"<p>" + safe_description + "</p>" if safe_description else ""}\n'
    '        </div>\n'
    '        """)\n'
    '\n'
    '\n'
    'def page_header(title, description="", icon="", eyebrow=None):\n'
    '    """Backward-compatible alias that also supports the eyebrow parameter."""\n'
    '    render_page_header(title, description, icon, eyebrow=eyebrow)\n'
    '\n'
)

new_content = content[:orphan_start] + replacement_text + content[orphan_end:]

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Successfully fixed theme.py!")

# Verify
with open(filepath, 'r', encoding='utf-8') as f:
    verify = f.read()

has_render = 'def render_page_header' in verify
has_page = 'def page_header' in verify
has_section = 'def render_section_header' in verify
print(f"render_page_header present: {has_render}")
print(f"page_header present: {has_page}")
print(f"render_section_header present: {has_section}")
</｜｜DSML｜｜parameter>
</create_file>
