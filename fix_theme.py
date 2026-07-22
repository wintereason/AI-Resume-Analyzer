# Fix corrupted theme.py
with open(r'c:/Users/suraj/OneDrive/Desktop/db/Data Science Course/Vocational Training project/ai_resume_analyzer/utils/theme.py', 'r') as f:
    content = f.read()

# Find the corrupted section
marker = "st.html(f\"<div class='progress-rail'>"
start = content.find(marker)
end = content.find('def render_section_header', start)

if start == -1 or end == -1:
    print("ERROR: Could not find corrupted section")
    exit(1)

print(f"Found corrupted section from {start} to {end}")
print(f"Old content fragment: ...{content[start:start+80]}...")

# Construct the correct replacement
correct = '''    st.html(f"<div class='progress-rail'>{''.join(items)}</div>")


def render_page_header(title, description="", icon="", eyebrow=None):
    """Render a premium page header."""
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
    """Backward-compatible alias that also supports the eyebrow parameter."""
    render_page_header(title, description, icon, eyebrow=eyebrow)


def render_section_header(title, description=None, icon=None):
'''

new_content = content[:start] + correct + content[end:]

# Write back
with open(r'c:/Users/suraj/OneDrive/Desktop/db/Data Science Course/Vocational Training project/ai_resume_analyzer/utils/theme.py', 'w') as f:
    f.write(new_content)

print("File fixed successfully!")

# Verify
with open(r'c:/Users/suraj/OneDrive/Desktop/db/Data Science Course/Vocational Training project/ai_resume_analyzer/utils/theme.py', 'r') as f:
    lines = f.readlines()

found_render_header = False
found_page_header = False
for i, l in enumerate(lines):
    if 'def render_page_header' in l:
        found_render_header = True
        print(f"Found render_page_header at line {i+1}")
    if 'def page_header' in l and 'def page_header' in l and 'Backward' in lines[i+1] if i+1 < len(lines) else '':
        found_page_header = True
        print(f"Found page_header at line {i+1}")

print(f"render_page_header present: {found_render_header}")
print(f"page_header present: {found_page_header}")
</｜｜DSML｜｜parameter>
</create_file>
