import streamlit as st

def render_skills_dashboard(skills_data):
    """
    Render a compact and stylish skill dashboard with category blocks,
    star ratings, and hoverable experience info.
    """
    st.subheader("🧠 Skills Overview")

    categories = skills_data.get("categories", [])
    if not categories:
        st.info("No skills data available.")
        return

    for category in categories:
        st.markdown(f"### {category['name']}")
        cols = st.columns(2)  # Two columns per category for better density

        for idx, skill in enumerate(category.get("skills", [])):
            name = skill.get("name", "Unnamed Skill")
            level = skill.get("level", 0)
            experience = skill.get("experience_years", "?")

            stars = "⭐" * level + "☆" * (10 - level)
            tooltip = f"{experience} years experience"

            skill_html = f"""
            <div title="{tooltip}" style="
                border: 1px solid #E0E0E0;
                border-radius: 10px;
                padding: 12px;
                margin-bottom: 10px;
                background-color: #FAFAFA;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            ">
                <div style="font-weight: 600; margin-bottom: 4px;">{name}</div>
                <div style="font-size: 1.1em; color: #FFC107;">{stars}</div>
            </div>
            """

            with cols[idx % 2]:
                st.markdown(skill_html, unsafe_allow_html=True)
