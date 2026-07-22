import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# ---------------------------------
# Shared Plotly Layout
# ---------------------------------
def apply_chart_layout(
    figure,
    title=None,
    height=400,
):
    figure.update_layout(
        title=title,
        height=height,
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Inter, sans-serif",
            size=13,
<<<<<<< HEAD
            color="#CBD5E1",
=======
            color="#475569",
>>>>>>> a1ff58d (Update UI and improve performance)
        ),
        legend_title_text="",
        hoverlabel=dict(
            font_size=13,
        ),
    )

    figure.update_xaxes(
        showgrid=False,
        zeroline=False,
    )

    figure.update_yaxes(
<<<<<<< HEAD
        gridcolor="rgba(148,163,184,0.15)",
=======
        gridcolor="rgba(67,86,122,0.10)",
>>>>>>> a1ff58d (Update UI and improve performance)
        zeroline=False,
    )

    return figure


# ---------------------------------
# ATS Distribution Bar Chart
# ---------------------------------
def create_ats_distribution_chart(data):
    df = pd.DataFrame(data)

    if df.empty:
        return None

    df = df.rename(
        columns={
            "score_range": "Score Range",
            "candidate_count": "Candidates",
            "resume_count": "Candidates",
        }
    )

    score_order = [
        "Below 50",
        "50-60",
        "61-70",
        "71-80",
        "81-90",
        "Above 90",
    ]

    df["Score Range"] = pd.Categorical(
        df["Score Range"],
        categories=score_order,
        ordered=True,
    )

    df = df.sort_values("Score Range")

    figure = px.bar(
        df,
        x="Score Range",
        y="Candidates",
        text="Candidates",
        title="ATS Score Distribution",
    )

    figure.update_traces(
<<<<<<< HEAD
=======
        marker=dict(color="#08AFC4", line=dict(color="#FFFFFF", width=1)),
>>>>>>> a1ff58d (Update UI and improve performance)
        textposition="outside",
        hovertemplate=("<b>%{x}</b><br>" "Candidates: %{y}" "<extra></extra>"),
    )

    return apply_chart_layout(
        figure,
        height=390,
    )


# ---------------------------------
# Candidate Status Donut Chart
# ---------------------------------
def create_status_donut_chart(data):
    df = pd.DataFrame(data)

    if df.empty:
        return None

    df = df.rename(
        columns={
            "status": "Status",
            "candidate_status": "Status",
            "candidate_count": "Candidates",
        }
    )

    figure = px.pie(
        df,
        names="Status",
        values="Candidates",
        hole=0.58,
        title="Candidate Status Distribution",
    )

    figure.update_traces(
<<<<<<< HEAD
=======
        marker=dict(colors=["#2867D8", "#08AFC4", "#15B878", "#F59E0B", "#EC5D8F", "#6846C7"]),
>>>>>>> a1ff58d (Update UI and improve performance)
        textposition="inside",
        textinfo="percent+label",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Candidates: %{value}<br>"
            "Percentage: %{percent}"
            "<extra></extra>"
        ),
    )

    figure.add_annotation(
        text=f"{int(df['Candidates'].sum())}<br>Candidates",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=16),
    )

    return apply_chart_layout(
        figure,
        height=390,
    )


# ---------------------------------
# Top Skills Horizontal Chart
# ---------------------------------
def create_top_skills_chart(data):
    df = pd.DataFrame(data)

    if df.empty:
        return None

    df = df.rename(
        columns={
            "skill": "Skill",
            "candidate_count": "Candidates",
        }
    )

    df = df.sort_values(
        "Candidates",
        ascending=True,
    )

    figure = px.bar(
        df,
        x="Candidates",
        y="Skill",
        orientation="h",
        text="Candidates",
        title="Most Common Candidate Skills",
    )

    figure.update_traces(
        textposition="outside",
        hovertemplate=("<b>%{y}</b><br>" "Candidates: %{x}" "<extra></extra>"),
    )

    return apply_chart_layout(
        figure,
        height=430,
    )


# ---------------------------------
# Job Role Distribution
# ---------------------------------
def create_job_role_chart(data):
    df = pd.DataFrame(data)

    if df.empty:
        return None

    df = df.rename(
        columns={
            "recommended_role": "Recommended Role",
            "candidate_count": "Candidates",
        }
    )

    df = df.sort_values(
        "Candidates",
        ascending=False,
    )

    figure = px.bar(
        df,
        x="Recommended Role",
        y="Candidates",
        text="Candidates",
        title="Recommended Job Roles",
    )

    figure.update_traces(
        textposition="outside",
        hovertemplate=("<b>%{x}</b><br>" "Candidates: %{y}" "<extra></extra>"),
    )

    figure.update_xaxes(
        tickangle=-25,
    )

    return apply_chart_layout(
        figure,
        height=430,
    )


# ---------------------------------
# ATS Gauge Chart
# ---------------------------------
def create_ats_gauge(score):
    try:
        score = float(score or 0)

    except (TypeError, ValueError):
        score = 0

    score = max(0, min(score, 100))

    figure = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            number={
                "suffix": "%",
                "font": {"size": 38},
            },
            title={
                "text": "Average ATS Performance",
                "font": {"size": 17},
            },
            gauge={
                "axis": {
                    "range": [0, 100],
                    "tickwidth": 1,
                },
                "bar": {
                    "thickness": 0.28,
                },
                "steps": [
                    {
                        "range": [0, 50],
                        "color": "rgba(239,68,68,0.25)",
                    },
                    {
                        "range": [50, 70],
                        "color": "rgba(245,158,11,0.25)",
                    },
                    {
                        "range": [70, 85],
                        "color": "rgba(59,130,246,0.25)",
                    },
                    {
                        "range": [85, 100],
                        "color": "rgba(34,197,94,0.25)",
                    },
                ],
                "threshold": {
                    "line": {
                        "width": 3,
                    },
                    "thickness": 0.75,
                    "value": score,
                },
            },
        )
    )

    return apply_chart_layout(
        figure,
        height=330,
    )
