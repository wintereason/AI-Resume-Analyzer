import html
import re

import streamlit as st

# ---------------------------------------------------------------------------
# Design tokens
# ---------------------------------------------------------------------------
COLORS = {
    "bg": "#F3F6FC",
    "sidebar": "#FFFFFF",
    "card": "#FFFFFF",
    "card_secondary": "#F7F9FD",
    "primary": "#2867D8",
    "cyan": "#08AFC4",
    "green": "#15B878",
    "amber": "#F59E0B",
    "red": "#EC5D8F",
    "purple": "#6846C7",
    "text": "#172033",
    "text_secondary": "#475569",
    "muted": "#718096",
    "border": "rgba(67, 86, 122, 0.14)",
    "border_strong": "rgba(40, 103, 216, 0.24)",
}

RADIUS = {
    "sm": "8px",
    "input": "10px",
    "card": "14px",
    "card_lg": "18px",
    "pill": "999px",
}

SHADOW = "0 16px 40px rgba(15, 23, 42, 0.08)"

AVATAR_SIZES = {
    "small": 36,
    "medium": 48,
    "large": 88,
}

STATUS_COLORS = {
    "under review": ("#2867D8", "Under Review"),
    "shortlisted": ("#08AFC4", "Shortlisted"),
    "interview scheduled": ("#F59E0B", "Interview Scheduled"),
    "selected": ("#15B878", "Selected"),
    "rejected": ("#EC5D8F", "Rejected"),
    "review required": ("#F59E0B", "Review Required"),
    "scheduled": ("#F59E0B", "Scheduled"),
    "completed": ("#15B878", "Completed"),
    "cancelled": ("#EC5D8F", "Cancelled"),
    "rescheduled": ("#F59E0B", "Rescheduled"),
    "candidate absent": ("#F59E0B", "Candidate Absent"),
    "active": ("#15B878", "Active"),
    "disabled": ("#718096", "Disabled"),
    "not assigned": ("#718096", "Not Assigned"),
}


def escape_html(value):
    """Escape user-controlled values before inserting into HTML."""
    return html.escape(str(value or ""), quote=True)


def get_initials(name):
    """Return up to two uppercase initials from a display name."""
    safe_name = str(name or "Candidate").strip()
    parts = [part for part in re.split(r"\s+", safe_name) if part]

    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()

    if parts:
        return parts[0][:2].upper()

    return "CA"


def _status_style(status):
    key = str(status or "under review").strip().lower()
    color, label = STATUS_COLORS.get(key, (COLORS["muted"], status or "Unknown"))
    return color, label


def apply_global_styles():
    """Apply centralized SaaS-style UI styling across all Streamlit pages."""
    c = COLORS
    r = RADIUS

    st.html(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
            :root {{
                --app-bg: {c["bg"]};
                --card-bg: {c["card"]};
                --card-secondary: {c["card_secondary"]};
                --primary: {c["primary"]};
                --text: {c["text"]};
                --muted: {c["muted"]};
                --border: {c["border"]};
                --shadow: {SHADOW};
            }}
            html, body, [class*="css"] {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            }}
            .stApp {{
                background: {c["bg"]};
                color: {c["text"]};
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            }}
            header[data-testid="stHeader"] {{
                background: transparent;
                visibility: hidden;
                height: 0;
            }}
            .block-container {{
                max-width: 1440px;
                padding-top: 8px;
                padding-bottom: 40px;
            }}
            h1, h2, h3, h4, h5 {{
                color: {c["text"]};
                letter-spacing: -0.02em;
                font-family: 'Inter', sans-serif;
            }}
            p, label, .stMarkdown, .stCaption {{
                color: {c["text_secondary"]};
            }}
            section[data-testid="stSidebar"] {{
                background: {c["sidebar"]};
                border-right: 1px solid {c["border"]};
            }}
            section[data-testid="stSidebar"] .block-container {{
                padding-top: 16px;
            }}
            section[data-testid="stSidebar"] div[data-testid="stSidebarNav"] {{
                display: none;
            }}
            .sidebar-nav-label {{
                color: {c["muted"]};
                font-size: 0.72rem;
                font-weight: 700;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                margin: 16px 0 8px 0;
                padding: 0 4px;
            }}
            div[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] {{
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 10px 12px;
                margin-bottom: 4px;
                border-radius: 12px;
                color: {c["text_secondary"]} !important;
                font-size: 0.88rem;
                font-weight: 600;
                text-decoration: none;
                border: 1px solid transparent;
                transition: background 0.18s ease, border-color 0.18s ease, transform 0.18s ease;
            }}
            div[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:hover {{
                background: rgba(79, 124, 255, 0.1);
                border-color: {c["border"]};
                transform: scale(1.02);
                color: {c["text"]} !important;
            }}
            div[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"][aria-current="page"] {{
                background: rgba(79, 124, 255, 0.16);
                border-color: rgba(79, 124, 255, 0.28);
                text-decoration: none;
                border: 1px solid transparent;
                transition: background 0.18s ease, border-color 0.18s ease, transform 0.18s ease;
            }}

            div[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:hover {{
                background: rgba(79, 124, 255, 0.1);
                border-color: {c["border"]};
                transform: scale(1.02);
                color: {c["text"]} !important;
            }}

            div[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"][aria-current="page"] {{
                background: rgba(79, 124, 255, 0.16);
                border-color: rgba(79, 124, 255, 0.28);
                color: {c["text"]} !important;
            }}

            /* Buttons */
            div[data-testid="stButton"] button,
            div[data-testid="stDownloadButton"] button,
            div[data-testid="stFormSubmitButton"] button {{
                min-height: 42px;
                border-radius: {r["input"]};
                font-weight: 650;
                border: 1px solid {c["border"]};
                transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
            }}

            div[data-testid="stButton"] button:hover,
            div[data-testid="stDownloadButton"] button:hover,
            div[data-testid="stFormSubmitButton"] button:hover {{
                transform: scale(1.02);
                box-shadow: 0 8px 20px rgba(79, 124, 255, 0.18);
            }}

            div[data-testid="stButton"] button[kind="primary"],
            div[data-testid="stFormSubmitButton"] button[kind="primary"] {{
                background: {c["primary"]};
                border-color: {c["primary"]};
                color: #fff;
            }}

            /* Inputs */
            div[data-baseweb="input"] > div,
            div[data-baseweb="select"] > div,
            div[data-baseweb="textarea"] > div {{
                border-radius: {r["input"]};
                border-color: {c["border"]};
                background: rgba(21, 31, 50, 0.85);
            }}

            /* Metrics fallback */
            div[data-testid="stMetric"] {{
                background: {c["card"]};
                border: 1px solid {c["border"]};
                border-radius: {r["card"]};
                padding: 16px;
                box-shadow: {SHADOW};
            }}

            div[data-testid="stMetric"] label {{
                color: {c["muted"]} !important;
                font-size: 0.8rem;
                font-weight: 600;
            }}

            /* Tables */
            div[data-testid="stDataFrame"] {{
                border: 1px solid {c["border"]};
                border-radius: {r["card"]};
                overflow: hidden;
                background: {c["card"]};
            }}

            /* Tabs */
            div[data-testid="stTabs"] button {{
                border-radius: {r["sm"]} {r["sm"]} 0 0;
                font-weight: 600;
            }}

            /* Expanders & alerts */
            div[data-testid="stExpander"] {{
                background: {c["card"]};
                border: 1px solid {c["border"]};
                border-radius: {r["card"]};
            }}

            div[data-testid="stAlert"] {{
                border-radius: {r["input"]};
                border: 1px solid {c["border"]};
            }}

            div[data-testid="stFileUploader"] {{
                border: 1px dashed {c["border_strong"]};
                border-radius: {r["card"]};
                padding: 12px;
                background: rgba(21, 31, 50, 0.55);
            }}

            div[data-testid="stProgress"] > div > div {{
                background: linear-gradient(90deg, {c["primary"]}, {c["cyan"]});
                border-radius: {r["pill"]};
            }}

            hr {{
                border-color: {c["border"]};
                margin: 24px 0;
            }}

            /* Component classes */
            .saas-page-header {{
                padding: 24px 28px;
                border-radius: {r["card_lg"]};
                background: linear-gradient(135deg, rgba(21,31,50,0.98), rgba(79,124,255,0.22));
                border: 1px solid {c["border_strong"]};
                margin-bottom: 24px;
                box-shadow: {SHADOW};
            }}

            .saas-page-header .eyebrow {{
                color: {c["cyan"]};
                font-size: 0.78rem;
                font-weight: 700;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                margin-bottom: 8px;
            }}

            .saas-page-header h1 {{
                margin: 0;
                font-size: 1.85rem;
                font-weight: 800;
            }}

            .saas-page-header p {{
                margin: 8px 0 0 0;
                color: {c["muted"]};
                font-size: 0.95rem;
                max-width: 720px;
            }}

            .dashboard-shell {{
                padding: 6px 2px 0 2px;
            }}

            .saas-section-header {{
                margin: 8px 0 16px 0;
            }}

            .saas-section-header h3 {{
                margin: 0;
                font-size: 1.1rem;
                font-weight: 700;
                color: {c["text"]};
            }}

            .saas-section-header p {{
                margin: 4px 0 0 0;
                color: {c["muted"]};
                font-size: 0.88rem;
            }}

            .saas-panel-card {{
                background: linear-gradient(135deg, rgba(21,31,50,0.97), rgba(17,24,39,0.95));
                border: 1px solid {c["border"]};
                border-radius: {r["card"]};
                padding: 18px 20px;
                box-shadow: {SHADOW};
                margin-bottom: 14px;
            }}

            .saas-panel-card h4 {{
                margin: 0 0 6px 0;
                color: {c["text"]};
                font-size: 0.98rem;
                font-weight: 700;
            }}

            .saas-panel-card .meta {{
                margin: 0;
                color: {c["muted"]};
                font-size: 0.84rem;
                line-height: 1.55;
            }}

            .saas-panel-card .pill-row {{
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                margin-top: 10px;
            }}

            .progress-rail {{
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
                margin: 6px 0 22px 0;
            }}

            .progress-step {{
                flex: 1;
                min-width: 130px;
                border: 1px solid {c["border"]};
                border-radius: {r["card"]};
                padding: 12px 14px;
                background: rgba(21, 31, 50, 0.6);
                transition: border-color 0.2s ease, transform 0.2s ease;
            }}

            .progress-step.active {{
                border-color: {c["border_strong"]};
                background: rgba(79, 124, 255, 0.15);
                transform: translateY(-1px);
            }}

            .progress-step.done {{
                border-color: rgba(34, 197, 94, 0.28);
                background: rgba(34, 197, 94, 0.1);
            }}

            .progress-step .step-dot {{
                width: 24px;
                height: 24px;
                border-radius: 999px;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                background: rgba(79, 124, 255, 0.14);
                color: {c["primary"]};
                font-size: 0.78rem;
                font-weight: 700;
                margin-bottom: 8px;
            }}

            .progress-step strong {{
                display: block;
                color: {c["text"]};
                font-size: 0.84rem;
                margin-bottom: 2px;
            }}

            .progress-step span {{
                color: {c["muted"]};
                font-size: 0.75rem;
            }}

            .saas-kpi-card {{
                background: linear-gradient(145deg, rgba(21, 31, 50, 0.98), rgba(30, 41, 59, 0.92));
                border: 1px solid {c["border"]};
                border-radius: {r["card_lg"]};
                padding: 24px;
                min-height: 148px;
                height: 100%;
                box-shadow: {SHADOW};
                position: relative;
                overflow: hidden;
                transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
            }}

            .saas-kpi-card::before {{
                content: '';
                position: absolute;
                inset: 0;
                background: linear-gradient(135deg, rgba(79, 124, 255, 0.12), transparent 60%);
                pointer-events: none;
            }}

            .saas-kpi-card:hover {{
                transform: translateY(-2px) scale(1.01);
                border-color: {c["border_strong"]};
                box-shadow: 0 12px 30px rgba(0, 0, 0, 0.24);
            }}

            .saas-kpi-top {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 12px;
            }}

            .saas-kpi-icon {{
                width: 36px;
                height: 36px;
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                background: rgba(79, 124, 255, 0.14);
                border: 1px solid rgba(79, 124, 255, 0.22);
                font-size: 1rem;
            }}

            .saas-kpi-label {{
                color: {c["muted"]};
                font-size: 0.8rem;
                font-weight: 600;
            }}

            .saas-kpi-value {{
                color: {c["text"]};
                font-size: 1.75rem;
                font-weight: 800;
                line-height: 1.1;
                margin-bottom: 4px;
            }}

            .saas-kpi-subtitle {{
                color: {c["muted"]};
                font-size: 0.78rem;
            }}

            .saas-kpi-trend {{
                font-size: 0.76rem;
                font-weight: 700;
                padding: 2px 8px;
                border-radius: {r["pill"]};
            }}

            .saas-kpi-trend.up {{
                color: {c["green"]};
                background: rgba(34, 197, 94, 0.12);
            }}

            .saas-kpi-trend.down {{
                color: {c["red"]};
                background: rgba(239, 68, 68, 0.12);
            }}

            .saas-kpi-trend.neutral {{
                color: {c["muted"]};
                background: rgba(148, 163, 184, 0.12);
            }}

            .saas-chart-card {{
                background: linear-gradient(145deg, rgba(21, 31, 50, 0.98), rgba(17, 24, 39, 0.96));
                border: 1px solid {c["border"]};
                border-radius: {r["card_lg"]};
                padding: 24px;
                box-shadow: {SHADOW};
                margin-bottom: 8px;
                backdrop-filter: blur(16px);
                transition: border-color 0.2s ease, transform 0.2s ease;
            }}

            .saas-chart-card:hover {{
                border-color: {c["border_strong"]};
                transform: translateY(-1px);
            }}

            .saas-chart-card h4 {{
                margin: 0 0 4px 0;
                font-size: 1rem;
                font-weight: 700;
            }}

            .saas-chart-card .chart-desc {{
                color: {c["muted"]};
                font-size: 0.84rem;
                margin-bottom: 12px;
            }}

            .saas-chart-insight {{
                margin-top: 12px;
                padding: 10px 12px;
                border-radius: {r["input"]};
                background: rgba(79, 124, 255, 0.08);
                border: 1px solid rgba(79, 124, 255, 0.16);
                color: {c["text_secondary"]};
                font-size: 0.84rem;
            }}

            .status-badge {{
                display: inline-block;
                padding: 4px 10px;
                border-radius: {r["pill"]};
                font-size: 0.74rem;
                font-weight: 700;
                letter-spacing: 0.02em;
                border: 1px solid transparent;
                white-space: nowrap;
            }}

            .ats-badge {{
                display: inline-block;
                padding: 4px 10px;
                border-radius: {r["pill"]};
                font-size: 0.74rem;
                font-weight: 700;
                background: rgba(79, 124, 255, 0.14);
                color: {c["primary"]};
                border: 1px solid rgba(79, 124, 255, 0.24);
            }}

            .candidate-row {{
                display: flex;
                align-items: center;
                gap: 14px;
                padding: 14px 16px;
                border: 1px solid {c["border"]};
                border-radius: {r["card"]};
                background: {c["card"]};
                margin-bottom: 10px;
                transition: border-color 0.2s ease, transform 0.2s ease;
            }}

            .candidate-row:hover {{
                border-color: {c["border_strong"]};
                transform: translateY(-1px);
            }}

            .candidate-avatar {{
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 800;
                color: {c["text"]};
                background: linear-gradient(135deg, {c["primary"]}, {c["cyan"]});
                border: 2px solid rgba(96, 165, 250, 0.28);
                flex-shrink: 0;
            }}

            .candidate-row-main {{
                flex: 1;
                min-width: 0;
            }}

            .candidate-row-name {{
                color: {c["text"]};
                font-weight: 700;
                font-size: 0.95rem;
                margin-bottom: 2px;
            }}

            .candidate-row-email {{
                color: {c["muted"]};
                font-size: 0.8rem;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }}

            .candidate-row-meta {{
                display: flex;
                flex-direction: column;
                align-items: flex-end;
                gap: 6px;
                flex-shrink: 0;
            }}

            .candidate-row-role {{
                color: {c["text_secondary"]};
                font-size: 0.78rem;
                text-align: right;
                max-width: 160px;
            }}

            .skill-chip {{
                display: inline-block;
                padding: 5px 10px;
                margin: 3px;
                border-radius: {r["pill"]};
                font-size: 0.78rem;
                font-weight: 600;
                background: rgba(79, 124, 255, 0.12);
                border: 1px solid rgba(79, 124, 255, 0.22);
                color: {c["primary"]};
            }}

            .skill-chip.matched {{
                background: rgba(34, 197, 94, 0.12);
                border-color: rgba(34, 197, 94, 0.24);
                color: {c["green"]};
            }}

            .skill-chip.missing {{
                background: rgba(239, 68, 68, 0.12);
                border-color: rgba(239, 68, 68, 0.24);
                color: {c["red"]};
            }}

            .empty-state {{
                text-align: center;
                padding: 36px 24px;
                border-radius: {r["card"]};
                border: 1px dashed {c["border_strong"]};
                background: rgba(21, 31, 50, 0.55);
            }}

            .empty-state .empty-icon {{
                font-size: 2rem;
                margin-bottom: 12px;
            }}

            .empty-state h4 {{
                margin: 0 0 8px 0;
                color: {c["text"]};
                font-size: 1.05rem;
            }}

            .empty-state p {{
                margin: 0;
                color: {c["muted"]};
                font-size: 0.9rem;
            }}

            .timeline-card {{
                border: 1px solid {c["border"]};
                border-radius: {r["card"]};
                padding: 14px 16px;
                background: {c["card"]};
                margin-bottom: 12px;
                transition: border-color 0.2s ease;
            }}

            .timeline-card:hover {{
                border-color: {c["border_strong"]};
            }}

            .info-card {{
                background: {c["card"]};
                border: 1px solid {c["border"]};
                border-radius: {r["card"]};
                padding: 16px 18px;
                box-shadow: {SHADOW};
            }}

            .info-card h4 {{
                margin: 0 0 8px 0;
                font-size: 0.95rem;
            }}

            .info-card p {{
                margin: 0;
                color: {c["text_secondary"]};
                font-size: 0.88rem;
            }}

            /* Login */
            .login-brand-panel {{
                background: linear-gradient(160deg, rgba(21,31,50,0.95), rgba(79,124,255,0.18));
                border: 1px solid {c["border"]};
                border-radius: {r["card_lg"]};
                padding: 40px 32px;
                min-height: 520px;
                box-shadow: {SHADOW};
            }}

            .login-brand-logo {{
                width: 56px;
                height: 56px;
                border-radius: 14px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.6rem;
                background: rgba(79, 124, 255, 0.16);
                border: 1px solid {c["border_strong"]};
                margin-bottom: 20px;
            }}

            .login-brand-panel h1 {{
                margin: 0 0 12px 0;
                font-size: 2rem;
                font-weight: 800;
            }}

            .login-brand-panel .tagline {{
                color: {c["text_secondary"]};
                font-size: 1rem;
                line-height: 1.6;
                margin-bottom: 28px;
            }}

            .login-feature {{
                display: flex;
                gap: 12px;
                margin-bottom: 16px;
                align-items: flex-start;
            }}

            .login-feature-icon {{
                width: 32px;
                height: 32px;
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                background: rgba(34, 211, 238, 0.12);
                border: 1px solid rgba(34, 211, 238, 0.2);
                flex-shrink: 0;
            }}

            .login-feature strong {{
                color: {c["text"]};
                display: block;
                font-size: 0.9rem;
                margin-bottom: 2px;
            }}

            .login-feature span {{
                color: {c["muted"]};
                font-size: 0.82rem;
            }}

            .login-form-card {{
                background: {c["card"]};
                border: 1px solid {c["border"]};
                border-radius: {r["card_lg"]};
                padding: 32px 28px;
                box-shadow: {SHADOW};
            }}

            .login-form-card h2 {{
                margin: 0 0 8px 0;
                font-size: 1.5rem;
            }}

            .login-form-card .subtitle {{
                color: {c["muted"]};
                font-size: 0.9rem;
                margin-bottom: 24px;
            }}

            .login-security {{
                margin-top: 16px;
                padding: 12px;
                border-radius: {r["input"]};
                background: rgba(34, 197, 94, 0.08);
                border: 1px solid rgba(34, 197, 94, 0.16);
                color: {c["text_secondary"]};
                font-size: 0.82rem;
            }}

            /* Sidebar account */
            .sidebar-account {{
                display: flex;
                gap: 12px;
                align-items: center;
                background: {c["card"]};
                border: 1px solid {c["border"]};
                border-radius: {r["card"]};
                padding: 12px;
                margin-bottom: 12px;
            }}

            .sidebar-account .name {{
                color: {c["text"]};
                font-weight: 700;
                font-size: 0.9rem;
                line-height: 1.2;
            }}

            .sidebar-account .meta {{
                color: {c["muted"]};
                font-size: 0.76rem;
                margin-top: 2px;
            }}

            .sidebar-status-row {{
                display: flex;
                flex-direction: column;
                gap: 8px;
                margin-top: 8px;
            }}

            .sidebar-status-item {{
                display: flex;
                align-items: center;
                gap: 8px;
                color: {c["muted"]};
                font-size: 0.78rem;
            }}

            .sidebar-dot {{
                width: 8px;
                height: 8px;
                border-radius: 50%;
                flex-shrink: 0;
            }}

            /* Top Navigation */
            .top-nav-shell {{
                background: linear-gradient(135deg, rgba(21, 31, 50, 0.98), rgba(30, 41, 59, 0.92));
                border: 1px solid {c["border"]};
                border-radius: {r["card_lg"]};
                padding: 12px 20px;
                margin-bottom: 24px;
                box-shadow: {SHADOW};
                backdrop-filter: blur(16px);
            }}

            .top-nav-brand {{
                display: flex;
                align-items: center;
                gap: 12px;
            }}

            .top-nav-logo {{
                width: 40px;
                height: 40px;
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                background: rgba(79, 124, 255, 0.16);
                border: 1px solid {c["border_strong"]};
                font-size: 1.2rem;
                flex-shrink: 0;
            }}

            .top-nav-title {{
                color: {c["text"]};
                font-size: 1rem;
                font-weight: 800;
                line-height: 1.2;
            }}

            .top-nav-subtitle {{
                color: {c["muted"]};
                font-size: 0.72rem;
                font-weight: 500;
            }}

            .top-nav-icon-btn {{
                width: 40px;
                height: 40px;
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                background: {c["card_secondary"]};
                border: 1px solid {c["border"]};
                font-size: 1rem;
                position: relative;
            }}

            .top-nav-notif-dot {{
                position: absolute;
                top: 8px;
                right: 8px;
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: {c["red"]};
                border: 2px solid {c["card"]};
            }}

            .top-nav-profile {{
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 6px 12px 6px 6px;
                border-radius: 12px;
                background: {c["card_secondary"]};
                border: 1px solid {c["border"]};
            }}

            .top-nav-profile-name {{
                color: {c["text"]};
                font-size: 0.84rem;
                font-weight: 700;
                line-height: 1.2;
            }}

            .top-nav-profile-role {{
                color: {c["muted"]};
                font-size: 0.72rem;
            }}

            div[data-testid="stTextInput"]:has(input[aria-label="nav_search"]) input {{
                background: {c["card_secondary"]} !important;
                border-color: {c["border"]} !important;
                border-radius: 12px !important;
                min-height: 42px;
                color: {c["text"]} !important;
            }}

            div[data-testid="stTextInput"]:has(input[aria-label="nav_search"]) input:focus {{
                border-color: {c["primary"]} !important;
                box-shadow: 0 0 0 2px rgba(79, 124, 255, 0.2) !important;
            }}

            /* Data Table */
            .saas-table-wrap {{
                background: {c["card"]};
                border: 1px solid {c["border"]};
                border-radius: {r["card_lg"]};
                overflow: hidden;
                box-shadow: {SHADOW};
            }}

            .saas-table-scroll {{
                overflow-x: auto;
                max-height: 420px;
                overflow-y: auto;
            }}

            .saas-table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 0.84rem;
            }}

            .saas-table thead {{
                position: sticky;
                top: 0;
                z-index: 2;
            }}

            .saas-table th {{
                background: {c["card_secondary"]};
                color: {c["muted"]};
                font-size: 0.72rem;
                font-weight: 700;
                letter-spacing: 0.06em;
                text-transform: uppercase;
                text-align: left;
                padding: 14px 16px;
                border-bottom: 1px solid {c["border"]};
                white-space: nowrap;
            }}

            .saas-table td {{
                padding: 14px 16px;
                color: {c["text_secondary"]};
                border-bottom: 1px solid {c["border"]};
                vertical-align: middle;
            }}

            .saas-table tbody tr:nth-child(even) {{
                background: rgba(30, 41, 59, 0.35);
            }}

            .saas-table tbody tr:hover {{
                background: rgba(79, 124, 255, 0.06);
            }}

            .saas-table .cell-candidate {{
                display: flex;
                align-items: center;
                gap: 12px;
            }}

            .saas-table .cell-name {{
                color: {c["text"]};
                font-weight: 700;
                font-size: 0.88rem;
            }}

            .saas-table .cell-email {{
                color: {c["muted"]};
                font-size: 0.76rem;
            }}

            .table-action-btn {{
                display: inline-flex;
                align-items: center;
                justify-content: center;
                padding: 6px 12px;
                border-radius: 8px;
                background: rgba(79, 124, 255, 0.12);
                border: 1px solid rgba(79, 124, 255, 0.24);
                color: {c["primary"]};
                font-size: 0.76rem;
                font-weight: 700;
            }}

            /* Interview Cards */
            .interview-card {{
                background: {c["card"]};
                border: 1px solid {c["border"]};
                border-radius: {r["card_lg"]};
                padding: 16px 18px;
                margin-bottom: 12px;
                box-shadow: {SHADOW};
                transition: transform 0.2s ease, border-color 0.2s ease;
            }}

            .interview-card:hover {{
                transform: scale(1.02);
                border-color: {c["border_strong"]};
            }}

            .interview-card-header {{
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                gap: 12px;
                margin-bottom: 10px;
            }}

            .interview-card-name {{
                color: {c["text"]};
                font-weight: 700;
                font-size: 0.92rem;
            }}

            .interview-card-role {{
                color: {c["muted"]};
                font-size: 0.78rem;
                margin-top: 2px;
            }}

            .interview-card-meta {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 8px 16px;
                margin-top: 10px;
            }}

            .interview-meta-item {{
                display: flex;
                flex-direction: column;
                gap: 2px;
            }}

            .interview-meta-label {{
                color: {c["muted"]};
                font-size: 0.68rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.04em;
            }}

            .interview-meta-value {{
                color: {c["text_secondary"]};
                font-size: 0.8rem;
                font-weight: 600;
            }}

            /* Activity Timeline */
            .activity-timeline {{
                position: relative;
                padding-left: 28px;
            }}

            .activity-timeline::before {{
                content: '';
                position: absolute;
                left: 11px;
                top: 8px;
                bottom: 8px;
                width: 2px;
                background: {c["border"]};
            }}

            .timeline-item {{
                position: relative;
                margin-bottom: 20px;
                padding: 16px 18px;
                background: {c["card"]};
                border: 1px solid {c["border"]};
                border-radius: {r["card_lg"]};
                box-shadow: {SHADOW};
                transition: transform 0.2s ease, border-color 0.2s ease;
            }}

            .timeline-item:hover {{
                transform: scale(1.01);
                border-color: {c["border_strong"]};
            }}

            .timeline-item::before {{
                content: '';
                position: absolute;
                left: -23px;
                top: 22px;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                background: var(--timeline-accent, {c["primary"]});
                border: 2px solid {c["bg"]};
                box-shadow: 0 0 0 2px var(--timeline-accent, {c["primary"]});
            }}

            .timeline-item-header {{
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                gap: 12px;
                flex-wrap: wrap;
                margin-bottom: 8px;
            }}

            .timeline-item-title {{
                color: {c["text"]};
                font-weight: 700;
                font-size: 0.9rem;
            }}

            .timeline-item-time {{
                color: {c["muted"]};
                font-size: 0.76rem;
                white-space: nowrap;
            }}

            .timeline-item-desc {{
                color: {c["text_secondary"]};
                font-size: 0.84rem;
                margin: 0 0 8px 0;
                line-height: 1.5;
            }}

            .timeline-item-actor {{
                color: {c["muted"]};
                font-size: 0.76rem;
                font-weight: 600;
            }}

            .panel-card-shell {{
                background: {c["card"]};
                border: 1px solid {c["border"]};
                border-radius: {r["card_lg"]};
                padding: 24px;
                box-shadow: {SHADOW};
            }}

            @media screen and (max-width: 900px) {{
                .block-container {{
                    padding-left: 16px;
                    padding-right: 16px;
                }}

                .saas-page-header {{
                    padding: 20px;
                }}

                .saas-kpi-value {{
                    font-size: 1.45rem;
                }}

                .login-brand-panel {{
                    min-height: auto;
                    margin-bottom: 16px;
                }}
            }}
        </style>
        """)


def render_progress_steps(steps, current_step=0):
    """Render a polished stepper for onboarding or multi-stage workflows."""
    if not steps:
        return

    items = []

    for index, step in enumerate(steps):
        label = str(step).strip() or f"Step {index + 1}"
        state = (
            "done"
            if index < current_step
            else "active" if index == current_step else "pending"
        )
        dot = "✓" if state == "done" else str(index + 1)
        items.append(f"""
            <div class="progress-step {state}">
                <div class="step-dot">{escape_html(dot)}</div>
                <strong>{escape_html(label)}</strong>
                <span>{escape_html('Complete' if state == 'done' else 'In progress' if state == 'active' else 'Pending')}</span>
            </div>
            """)

    st.html(f"<div class='progress-rail'>{''.join(items)}</div>")


def render_page_header(title, description="", icon="", eyebrow=None):
    """Render a premium page header."""
    safe_title = escape_html(title)
    safe_description = escape_html(description)
    safe_icon = f"{escape_html(icon)} " if icon else ""
    eyebrow_html = (
        f'<div class="eyebrow">{escape_html(eyebrow)}</div>' if eyebrow else ""
    )

    description_html = f"<p>{safe_description}</p>" if safe_description else ""
    st.html(f"""
        <div class="saas-page-header">
            {eyebrow_html}
            <h1>{safe_icon}{safe_title}</h1>
            {description_html}
        </div>
        """)


def page_header(title, description="", icon="", eyebrow=None):
    """Backward-compatible page-header alias."""
    render_page_header(title, description, icon, eyebrow=eyebrow)


def render_section_header(title, description=None, icon=None):
    """Render a section heading."""
    safe_icon = f"{escape_html(icon)} " if icon else ""
    safe_title = escape_html(title)
    desc_html = f"<p>{escape_html(description)}</p>" if description else ""

    st.html(f"""
        <div class="saas-section-header">
            <h3>{safe_icon}{safe_title}</h3>
            {desc_html}
        </div>
        """)


def section_header(title, description="", icon=""):
    """Backward-compatible alias."""
    render_section_header(title, description or None, icon or None)


def render_kpi_card(
    label,
    value,
    icon="",
    subtitle=None,
    trend=None,
    trend_direction=None,
):
    """Render a custom KPI card with optional trend indicator."""
    trend_html = ""

    if trend:
        direction = (trend_direction or "neutral").lower()
        if direction not in {"up", "down", "neutral"}:
            direction = "neutral"

        trend_html = (
            f'<span class="saas-kpi-trend {direction}">{escape_html(trend)}</span>'
        )

    st.html(f"""
        <div class="saas-kpi-card">
            <div class="saas-kpi-top">
                <div class="saas-kpi-icon">{escape_html(icon)}</div>
                {trend_html}
            </div>
            <div class="saas-kpi-label">{escape_html(label)}</div>
            <div class="saas-kpi-value">{escape_html(value)}</div>
            {"<div class='saas-kpi-subtitle'>" + escape_html(subtitle) + "</div>" if subtitle else ""}
        </div>
        """)


def render_kpi_row(cards):
    """Render a responsive row of KPI cards."""
    columns = st.columns(len(cards))

    for column, card in zip(columns, cards):
        with column:
            render_kpi_card(
                label=card.get("label", ""),
                value=card.get("value", ""),
                icon=card.get("icon", ""),
                subtitle=card.get("subtitle"),
                trend=card.get("trend"),
                trend_direction=card.get("trend_direction"),
            )


def render_status_badge(status):
    """Render a colored recruitment status badge."""
    color, label = _status_style(status)

    st.html(f"""
        <span class="status-badge"
              style="color:{color};background:{color}22;border-color:{color}44;">
            {escape_html(label)}
        </span>
        """)


def render_ats_badge(score):
    """Render an ATS score badge."""
    try:
        numeric = float(score or 0)
    except (TypeError, ValueError):
        numeric = 0.0

    st.html(f'<span class="ats-badge">{escape_html(f"{numeric:.1f}%")}</span>')


def render_skill_chip(skill, variant=None):
    """Render a single skill chip."""
    css_class = "skill-chip"

    if variant in {"matched", "missing"}:
        css_class += f" {variant}"

    st.html(f'<span class="{css_class}">{escape_html(skill)}</span>')


def render_skill_chips(skills, variant=None):
    """Render multiple skill chips."""
    skill_list = skills or []

    if not skill_list:
        st.caption("No skills available.")
        return

    css_class = "skill-chip"
    if variant in {"matched", "missing"}:
        css_class += f" {variant}"

    chips_html = "".join(
        f'<span class="{css_class}">{escape_html(skill)}</span>' for skill in skill_list
    )

    st.html(f'<div style="line-height:2.1;">{chips_html}</div>')


def render_candidate_avatar(name, size="medium"):
    """Render a candidate avatar with initials."""
    pixel_size = AVATAR_SIZES.get(size, AVATAR_SIZES["medium"])
    initials = escape_html(get_initials(name))
    font_size = max(0.72, pixel_size / 52)

    st.html(f"""
        <div class="candidate-avatar"
             style="width:{pixel_size}px;height:{pixel_size}px;font-size:{font_size:.2f}rem;">
            {initials}
        </div>
        """)


def render_candidate_row(name, email, ats_score, role, status):
    """Render a polished candidate list row."""
    color, _ = _status_style(status)
    initials = escape_html(get_initials(name))

    st.html(f"""
        <div class="candidate-row">
            <div class="candidate-avatar"
                 style="width:40px;height:40px;font-size:0.78rem;">
                {initials}
            </div>
            <div class="candidate-row-main">
                <div class="candidate-row-name">{escape_html(name)}</div>
                <div class="candidate-row-email">{escape_html(email)}</div>
            </div>
            <div class="candidate-row-meta">
                <span class="ats-badge">{escape_html(f"{float(ats_score or 0):.1f}%")}</span>
                <span class="status-badge"
                      style="color:{color};background:{color}22;border-color:{color}44;">
                    {escape_html(status or "Under Review")}
                </span>
                <div class="candidate-row-role">{escape_html(role or "Not Assigned")}</div>
            </div>
        </div>
        """)


def render_empty_state(title, message, icon="📭"):
    """Render a product-style empty state."""
    st.html(f"""
        <div class="empty-state">
            <div class="empty-icon">{escape_html(icon)}</div>
            <h4>{escape_html(title)}</h4>
            <p>{escape_html(message)}</p>
        </div>
        """)


def render_info_card(title, content, icon=None):
    """Render a compact informational card."""
    safe_icon = f"{escape_html(icon)} " if icon else ""

    st.html(f"""
        <div class="info-card">
            <h4>{safe_icon}{escape_html(title)}</h4>
            <p>{escape_html(content)}</p>
        </div>
        """)


def render_chart_card(title, description=None, insight=None):
    """Open a chart card container. Call close_chart_card() after the chart."""
    desc_html = (
        f'<div class="chart-desc">{escape_html(description)}</div>'
        if description
        else ""
    )

    st.markdown(
        f"""
        <div class="saas-chart-card">
            <h4>{escape_html(title)}</h4>
            {desc_html}
        """,
        unsafe_allow_html=True,
    )

    return insight


def close_chart_card(insight=None):
    """Close a chart card and optionally render insight text."""
    insight_html = (
        f'<div class="saas-chart-insight">{escape_html(insight)}</div>'
        if insight
        else ""
    )

    st.markdown(f"{insight_html}</div>", unsafe_allow_html=True)


def render_timeline_item(
    title,
    description,
    performed_by=None,
    created_at=None,
    icon="🔹",
    accent_color=None,
    timestamp=None,
    actor=None,
    color=None,
):
    """Render a timeline event card."""
    event_color = color or accent_color or COLORS["primary"]
    event_time = timestamp or created_at or ""
    event_actor = actor or performed_by or "System"

    st.html(f"""
        <div class="timeline-card" style="border-left: 3px solid {event_color};">
            <div style="display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;">
                <strong style="color:{COLORS["text"]};">
                    {escape_html(icon)} {escape_html(title)}
                </strong>
                <span style="color:{COLORS["muted"]};font-size:0.8rem;">
                    {escape_html(event_time)}
                </span>
            </div>
            <p style="margin:8px 0;color:{COLORS["text_secondary"]};font-size:0.88rem;">
                {escape_html(description)}
            </p>
            <span style="color:{COLORS["muted"]};font-size:0.78rem;">
                {escape_html(event_actor)}
            </span>
        </div>
        """)


def count_status(status_records, target_status):
    """Count candidates for a given status from distribution records."""
    target = target_status.strip().lower()

    for record in status_records or []:
        status_name = str(
            record.get("candidate_status") or record.get("status") or ""
        ).strip()

        if status_name.lower() == target:
            return int(record.get("candidate_count") or record.get("count") or 0)

    return 0


ACTIVITY_ACCENT_COLORS = {
    "resume_uploaded": COLORS["primary"],
    "resume_saved": COLORS["cyan"],
    "candidate_shortlisted": COLORS["green"],
    "candidate_selected": "#10B981",
    "candidate_rejected": COLORS["red"],
    "status_updated": COLORS["amber"],
    "interview_scheduled": COLORS["amber"],
    "interview_status_updated": COLORS["cyan"],
    "interview_rescheduled": COLORS["amber"],
    "interview_deleted": COLORS["red"],
    "email_sent": COLORS["primary"],
    "offer_sent": COLORS["green"],
}


def _badge_html(status):
    """Return HTML for a status badge."""
    color, label = _status_style(status)
    return (
        f'<span class="status-badge" '
        f'style="color:{color};background:{color}22;border-color:{color}44;">'
        f"{escape_html(label)}</span>"
    )


def render_top_navbar(search_key="nav_search", logout_key="nav_logout"):
    """Render the executive top navigation bar."""
    from auth import logout_user

    user_name = st.session_state.get("user_name") or "User"
    user_role = st.session_state.get("user_role") or "Recruiter"
    initials = escape_html(get_initials(user_name))
    c = COLORS

    brand_col, search_col, notif_col, profile_col, logout_col = st.columns(
        [2.2, 4.2, 0.5, 1.6, 0.9]
    )

    with brand_col:
        st.markdown(
            f"""
            <div class="top-nav-shell" style="margin-bottom:0;padding:10px 16px;">
                <div class="top-nav-brand">
                    <div class="top-nav-logo">🤖</div>
                    <div>
                        <div class="top-nav-title">AI Resume Analyzer</div>
                        <div class="top-nav-subtitle">Recruitment Intelligence Platform</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with search_col:
        st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
        st.text_input(
            "nav_search",
            placeholder="Search candidates, roles, skills...",
            label_visibility="collapsed",
            key=search_key,
        )

    with notif_col:
        st.markdown(
            f"""
            <div style="margin-top:10px;">
                <div class="top-nav-icon-btn">
                    🔔
                    <span class="top-nav-notif-dot"></span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with profile_col:
        st.markdown(
            f"""
            <div style="margin-top:6px;">
                <div class="top-nav-profile">
                    <div class="candidate-avatar"
                         style="width:32px;height:32px;font-size:0.72rem;">
                        {initials}
                    </div>
                    <div>
                        <div class="top-nav-profile-name">{escape_html(user_name)}</div>
                        <div class="top-nav-profile-role">{escape_html(user_role)}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with logout_col:
        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
        if st.button("Logout", key=logout_key, type="secondary", width="stretch"):
            logout_user()
            st.switch_page("pages/0_Login.py")


def render_candidates_table(candidates):
    """Render a modern striped candidates table with avatars and badges."""
    if not candidates:
        return

    rows = []

    for candidate in candidates:
        name = candidate.get("name") or "Unknown Candidate"
        email = candidate.get("email") or "Not Available"
        ats_score = candidate.get("ats_score")
        role = candidate.get("recommended_role") or "Not Assigned"
        status = candidate.get("status") or "Under Review"
        initials = escape_html(get_initials(name))

        try:
            ats_text = f"{float(ats_score or 0):.1f}%"
        except (TypeError, ValueError):
            ats_text = "0.0%"

        rows.append(f"""
            <tr>
                <td>
                    <div class="cell-candidate">
                        <div class="candidate-avatar"
                             style="width:36px;height:36px;font-size:0.72rem;">
                            {initials}
                        </div>
                        <div>
                            <div class="cell-name">{escape_html(name)}</div>
                            <div class="cell-email">{escape_html(email)}</div>
                        </div>
                    </div>
                </td>
                <td><span class="ats-badge">{escape_html(ats_text)}</span></td>
                <td>{_badge_html(status)}</td>
                <td style="color:{COLORS["text_secondary"]};">{escape_html(role)}</td>
                <td><span class="table-action-btn">View</span></td>
            </tr>
            """)

    st.html(f"""
        <div class="saas-table-wrap">
            <div class="saas-table-scroll">
                <table class="saas-table">
                    <thead>
                        <tr>
                            <th>Candidate</th>
                            <th>ATS Score</th>
                            <th>Status</th>
                            <th>Recommended Role</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {"".join(rows)}
                    </tbody>
                </table>
            </div>
        </div>
        """)


def render_interview_card(
    candidate_name,
    role,
    interview_date,
    interview_time,
    mode,
    status,
    mode_icon="📅",
):
    """Render a compact upcoming interview card."""
    color, status_label = _status_style(status)

    st.html(f"""
        <div class="interview-card">
            <div class="interview-card-header">
                <div>
                    <div class="interview-card-name">{escape_html(candidate_name)}</div>
                    <div class="interview-card-role">{escape_html(role)}</div>
                </div>
                <span class="status-badge"
                      style="color:{color};background:{color}22;border-color:{color}44;">
                    {escape_html(status_label)}
                </span>
            </div>
            <div class="interview-card-meta">
                <div class="interview-meta-item">
                    <span class="interview-meta-label">Date</span>
                    <span class="interview-meta-value">{escape_html(interview_date)}</span>
                </div>
                <div class="interview-meta-item">
                    <span class="interview-meta-label">Time</span>
                    <span class="interview-meta-value">{escape_html(interview_time)}</span>
                </div>
                <div class="interview-meta-item">
                    <span class="interview-meta-label">Mode</span>
                    <span class="interview-meta-value">{escape_html(mode_icon)} {escape_html(mode)}</span>
                </div>
                <div class="interview-meta-item">
                    <span class="interview-meta-label">Role</span>
                    <span class="interview-meta-value">{escape_html(role)}</span>
                </div>
            </div>
        </div>
        """)


def render_activity_timeline(activities, icon_resolver=None):
    """Render a vertical recruitment activity timeline."""
    if not activities:
        return

    items = []

    for activity in activities:
        activity_type = activity.get("activity_type") or "general_activity"
        icon = icon_resolver(activity_type) if icon_resolver else "🔹"
        accent = ACTIVITY_ACCENT_COLORS.get(activity_type, COLORS["primary"])
        title = activity.get("activity_title") or "Candidate Activity"
        description = (
            f"Candidate: {activity.get('candidate_name') or 'Unknown Candidate'}"
        )
        actor = activity.get("performed_by_name") or "System"
        timestamp = activity.get("created_at")

        if timestamp is not None:
            try:
                timestamp = timestamp.strftime("%d %b %Y, %I:%M %p")
            except AttributeError:
                timestamp = str(timestamp)
        else:
            timestamp = ""

        items.append(f"""
            <div class="timeline-item" style="--timeline-accent:{accent};">
                <div class="timeline-item-header">
                    <div class="timeline-item-title">{escape_html(icon)} {escape_html(title)}</div>
                    <div class="timeline-item-time">{escape_html(timestamp)}</div>
                </div>
                <p class="timeline-item-desc">{escape_html(description)}</p>
                <div class="timeline-item-actor">By {escape_html(actor)}</div>
            </div>
            """)

    st.html(f"<div class='activity-timeline'>{''.join(items)}</div>")
