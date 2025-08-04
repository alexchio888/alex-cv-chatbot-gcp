import streamlit as st

def render_skills_dashboard(skills_data):
    """
    Render a skills overview dashboard in Streamlit with two-column layout.
    """
    st.subheader("🧠 Skills Overview")

    categories = skills_data.get("categories", [])

    if not categories:
        st.info("No skills data available.")
        return

    for category in categories:
        st.markdown(f"### {category['name']}")

        col1, col2 = st.columns(2)

        skills = category.get("skills", [])
        half = (len(skills) + 1) // 2

        for idx, skill in enumerate(skills):
            target_col = col1 if idx < half else col2
            with target_col:
                render_skill_row(skill)


def render_skill_row(skill):
    name = skill.get("name", "Unnamed Skill")
    level = skill.get("level", 0)
    exp = skill.get("experience_years", "?")

    stars_html = ''.join([
        f'<span style="font-size: 1.2em; color: gold;">⭐</span>' if i < level
        else f'<span style="font-size: 1.2em; color: #ccc;">☆</span>'
        for i in range(10)
    ])

    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; align-items: center;
                    padding: 6px 10px; margin-bottom: 4px; border: 1px solid #e0e0e0;
                    border-radius: 8px;">
            <div>{stars_html}</div>
            <div style="text-align: right; margin-left: 12px;">
                <strong>{name}</strong><br>
                <span style="font-size: 0.85em; color: gray;">{exp} years</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
