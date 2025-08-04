import streamlit as st
import plotly.graph_objects as go

def render_skills_dashboard(skills_data):
    """
    Render a skills overview dashboard in Streamlit.

    Args:
        skills_data (dict): Skills JSON data with structure:
            {
              "title": str,
              "categories": [
                {
                  "name": str,
                  "skills": [
                    {"name": str, "level": int (1-5), "experience_years": int (optional)},
                    ...
                  ]
                },
                ...
              ]
            }
    """
    st.subheader("🧠 Skills Overview")

    categories = skills_data.get("categories", [])

    if not categories:
        st.info("No skills data available.")
        return

    # Prepare data for average skill level per category
    categories_names = [cat["name"] for cat in categories]
    avg_levels = []
    for cat in categories:
        levels = [skill["level"] for skill in cat["skills"] if "level" in skill]
        avg_level = sum(levels) / len(levels) if levels else 0
        avg_levels.append(avg_level)

    # Plot average skill level bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=categories_names,
            y=avg_levels,
            text=[f"{lvl:.1f}" for lvl in avg_levels],
            textposition="auto",
            marker_color='royalblue'
        )
    ])
    fig.update_layout(
        yaxis=dict(title="Average Skill Level", range=[0, 5]),
        xaxis=dict(title="Skill Categories"),
        title="Average Skill Level by Category",
        template="plotly_white",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

    # Detailed skill listing with stars and experience
    st.markdown("#### Detailed Skills")
    for cat in categories:
        st.markdown(f"**{cat['name']}**")
        for skill in cat["skills"]:
            level = skill.get("level", 0)
            stars = "⭐" * level + "☆" * (5 - level)
            exp = skill.get("experience_years", "?")
            st.markdown(f"- {skill['name']}: {stars} ({exp} years experience)")
