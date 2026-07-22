# -*- coding: utf-8 -*-
import sys

filepath = r'c:/Users/suraj/OneDrive/Desktop/db/Data Science Course/Vocational Training project/ai_resume_analyzer/utils/theme.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the corrupted section - search for the broken fragment
# The correct code should end with: st.html(f"<div class='progress-rail'>{''.join(items)}</div>")
# Then comes render_page_header function
# Then comes page_header function
# Then render_section_header

# Find the broken marker (the HTML that shouldn't be there)
broken_start_marker =  '{eyebrow_html}\n            <h1>{safe_icon}{safe_title}</h1>'
broken_end_marker = 'def render_section_header'

idx_start = content.find(broken_start_marker)
idx_end = content.find(broken_end_marker)

if idx_start == -1 or idx_end == -1:
    print("Could not find broken section markers")
    print(f"start found: {idx_start}")
    print(f"end found: {idx_end}")
    # Print debug info
    st_pos = content.find('st.html(f"<div class')
    print(f"st.html pos: {st_pos}")
    if st_pos >= 0:
        print(content[st_pos:st_pos+200])
    sys.exit(1)

# Find the beginning of the broken fragment - go back to find where render_page_header was lost
# Look backwards from broken_start_marker for "st.html(f" which is the last valid line
search_from = idx_start - 200
sub = content[search_from:idx_start]
last_valid_end = sub.rfind('st.html(f"<div class=\\'progress-rail')
if last_valid_end == -1:
    last_valid_end = sub.rfind('st.html(f"<div')
if last_valid_end == -1:
    # Try another approach - find the last .html( call before the broken part
    last_valid_end = sub.rfind('st.html(')
if last_valid_end == -1:
    # Just use search_from + something reasonable
    print("Could not find boundary, using fallback")
    # Find "st.html(f" before the broken section
    search_area = content[:idx_start]
    stpos = search_area.rfind('st.html(f"')
    if stpos >= 0:
        # Find the end of this st.html call
        close_paren = search_area.find(')', stpos)
        if close_paren >= 0:
            # Actually let's just find the full line
            line_start = search_area.rfind('\n', 0, stpos) + 1
            last_valid_end = line_start
        else:
            last_valid_end = stpos
    else:
        print("Cannot fix - cannot find boundary")
        sys.exit(1)

# Now construct the replacement
replacement_good = '''    st.html(f"<div class='progress-rail'>{''.join(items)}</div>")


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

# Find the actual start - the line containing the last valid st.html call
# Before the broken part
valid_st_html = content[:idx_start].rstrip()
# Find last line that looks like it ends with ')'
lines_before = content[:idx_start].split('\n')
# The problematic fragment starts somewhere after the last valid function
# Let's just find where "            {eyebrow_html}" appears and work backwards

# Simpler approach: Find what's between render_progress_steps end and render_section_header
# and replace it entirely
pp_start = content.find('def render_progress_steps')
pp_end = content.find('\ndef render_section_header', pp_start)
if pp_end == -1:
    pp_end = idx_end

if pp_end > 0:
    # Find the end of render_progress_steps function
    # It ends with st.html(f"<div class='progress-rail'>...")
    # Then there might be blank lines
    # Find the last line before render_section_header
    
    # The render_progress_steps ends at line containing the st.html call
    # Everything between there and render_section_header is what got corrupted
    
    # Find where the st.html call for progress_steps ends 
    # (it's the last valid code before the broken part)
    last_code = content[:pp_end].rstrip()
    # Find the last ')'
    last_paren = last_code.rfind(')')
    if last_paren > 0:
        # The code up to last_paren+1 is valid
        valid_end = last_paren + 1
        corrupted = content[valid_end:pp_end]
        
        new_content = content[:valid_end] + '\n\n\n' + replacement_good + content[pp_end + len('\ndef render_section_header'):]
        # Adjust: make sure we don't duplicate "def render_section_header"
        # The replacement_good ends with "def render_section_header" so we need to
        # skip the original one
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("File fixed successfully!")
    else:
        print("Could not find end of progress_steps function")
else:
    print("Could not find boundaries")
</｜｜DSML｜｜parameter>
</create_file>
