

filepath = r'c:/Users/suraj/OneDrive/Desktop/db/Data Science Course/Vocational Training project/ai_resume_analyzer/utils/theme.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the broken section
# It starts with orphan '{eyebrow_html}' after render_progress_steps
orphan_start = content.find('            {eyebrow_html}')
orphan_end = content.find('def render_section_header', orphan_start)

if orphan_start == -1 or orphan_end == -1:
    print("ERROR: Could not find corrupted section")
    sys.exit(1)

# Build the replacement text line by line to avoid any issues
replacement = []
replacement.append('def render_page_header(title, description="", icon="", eyebrow=None):')
replacement.append('    """Render a premium page header."""')
replacement.append('    safe_title = escape_html(title)')
replacement.append('    safe_description = escape_html(description)')
replacement.append('    safe_icon = f"{escape_html(icon)} " if icon else ""')
replacement.append('    eyebrow_html = (')
replacement.append("        f'<div class=\"eyebrow\">{escape_html(eyebrow)}</div>' if eyebrow else \"\"")
replacement.append('    )')
replacement.append('')
replacement.append('    st.html(f"""')
replacement.append('        <div class="saas-page-header">')
replacement.append('            {eyebrow_html}')
replacement.append('            <h1>{safe_icon}{safe_title}</h1>')
replacement.append('            {"<p>" + safe_description + "</p>" if safe_description else ""}')
replacement.append('        </div>')
replacement.append('        """)')
replacement.append('')
replacement.append('')
replacement.append('def page_header(title, description="", icon="", eyebrow=None):')
replacement.append('    """Backward-compatible alias that also supports the eyebrow parameter."""')
replacement.append('    render_page_header(title, description, icon, eyebrow=eyebrow)')
replacement.append('')

new_content = content[:orphan_start] + chr(10).join(replacement) + content[orphan_end:]

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("SUCCESS: Fixed theme.py!")

# Verify
with open(filepath, 'r', encoding='utf-8') as f:
    verify = f.read()

print(f"render_page_header present: {'def render_page_header' in verify}")
print(f"page_header present: {'def page_header' in verify}")
print(f"render_section_header present: {'def render_section_header' in verify}")

# Check no orphan eyebrow_html remains
print(f"orphan eyebrow_html remaining: {'            {eyebrow_html}' in verify}")
</absolute_path>
</create_file>
