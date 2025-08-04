import streamlit as st
import plotly.graph_objects as go

def render_skills_dashboard(skills_data):
    """
    Render a skills overview dashboard using bar charts per skill category.
    Args:
        skills_data (dict): Skills JSON structure with:
            {
              "title": str,
              "categories": [
                {
                  "name": str,
                  "skills": [
                    {"name": str, "level": int (1–10), "experience_years": float (optional)},
                    ...
                  ]
                },
                ...
              ]
            }
    """
    categories = skills_data.get("categories", [])
    if not categories:
        st.info("No skills data available.")
        return

    for category in categories:
        st.markdown(f"### {category['name']}")
        skills = category.get("skills", [])
        if not skills:
            st.markdown("_No skills listed._")
            continue

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=[skill["level"] for skill in skills],
            y=[skill["name"] for skill in skills],
            orientation='h',
            marker=dict(color='lightskyblue'),
            hovertext=[
                f"{skill.get('experience_years', '?')} years experience"
                for skill in skills
            ],
            hoverinfo='text+x'
        ))

        fig.update_layout(
            xaxis=dict(title='Skill Level (1–10)', range=[0, 10]),
            yaxis=dict(autorange="reversed"),  # Reverse to show top-down
            margin=dict(l=80, r=20, t=30, b=30),
            height=40 * len(skills) + 60,
            template="plotly_white",
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)
