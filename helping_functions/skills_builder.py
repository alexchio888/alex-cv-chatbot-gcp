import streamlit as st
import plotly.graph_objects as go

def render_skills_dashboard(skills_data):
    st.subheader("🧠 Skills Overview")

    categories = skills_data.get("categories", [])
    if not categories:
        st.info("No skills data available.")
        return

    for category in categories:
        st.markdown(f"#### {category['name']}")

        fig = go.Figure()

        for skill in category.get("skills", []):
            fig.add_trace(go.Bar(
                x=[skill["level"]],
                y=[skill["name"]],
                orientation='h',
                hovertemplate=f"{skill['experience_years']} years experience",
                marker=dict(
                    color="#1f77b4",
                    line=dict(color='rgba(0,0,0,0)', width=1)
                ),
                text=[f"{skill['level']}/10"],
                textposition='outside',
                width=0.4
            ))

        fig.update_layout(
            height=300 + len(category["skills"]) * 20,
            xaxis=dict(title="Skill Level", range=[0, 10]),
            yaxis=dict(autorange="reversed"),
            margin=dict(l=50, r=20, t=20, b=30),
            plot_bgcolor="#f9f9f9",
            paper_bgcolor="#f9f9f9",
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)
