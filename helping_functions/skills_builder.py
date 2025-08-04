import streamlit as st

def render_skills_dashboard(skills_data):
    st.subheader("🧠 Skills Overview")

    categories = skills_data.get("categories", [])
    if not categories:
        st.info("No skills data available.")
        return

    for category in categories:
        st.markdown(f"### {category['name']}")

        for skill in category["skills"]:
            render_skill_row(skill)

        st.markdown("---")


def render_skill_row(skill):
    name = skill.get("name", "Unnamed Skill")
    level = skill.get("level", 0)
    exp = skill.get("experience_years", "?")

    stars = "⭐" * level + "☆" * (10 - level)

    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; align-items: center;
                    padding: 6px 10px; border-bottom: 1px solid #DDD;">
            <div style="white-space: nowrap; font-family: monospace;">{stars}</div>
            <div style="text-align: right;">
                <strong>{name}</strong><br>
                <span style="font-size: 0.85em; color: gray;">{exp} years</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
