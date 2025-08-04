import streamlit as st

def render_skills_dashboard(skills_data):
    st.subheader("🧠 Skills Overview")

    categories = skills_data.get("categories", [])
    if not categories:
        st.info("No skills data available.")
        return

    for category in categories:
        st.markdown(f"### {category['name']}")
        cols = st.columns(2)

        for idx, skill in enumerate(category["skills"]):
            with cols[idx % 2]:
                render_skill_card(skill)


def render_skill_card(skill):
    name = skill.get("name", "Unnamed Skill")
    level = skill.get("level", 0)
    exp = skill.get("experience_years", "?")

    stars = "⭐" * level + "☆" * (10 - level)

    st.markdown(
        f"""
        <div style="
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 12px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.08);
            margin-bottom: 10px;
        ">
            <strong>{name}</strong><br>
            <abbr title='{exp} years experience'>{stars}</abbr>
        </div>
        """,
        unsafe_allow_html=True
    )
