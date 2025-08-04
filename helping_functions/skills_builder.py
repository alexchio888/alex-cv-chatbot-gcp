import streamlit as st

def render_skills_dashboard(skills_data):
    """
    Render a compact, clear skill block layout with star ratings and experience tooltips.
    """
    st.subheader("🧠 Skills Overview")

    categories = skills_data.get("categories", [])
    if not categories:
        st.info("No skills data available.")
        return

    for category in categories:
        st.markdown(f"### {category['name']}")
        cols = st.columns(2)  # Two-column layout for compact view
        for idx, skill in enumerate(category.get("skills", [])):
            name = skill.get("name", "Unnamed Skill")
            level = skill.get("level", 0)
            experience = skill.get("experience_years", None)

            stars = "⭐" * level + "☆" * (10 - level)

            tooltip = f"{experience} years experience" if experience is not None else "Experience not available"
            with cols[idx % 2]:
                st.markdown(
                    f"""
                    <div style="margin-bottom: 8px;">
                        <strong title="{tooltip}">{name}</strong><br>
                        <span style="font-size: 1.1em;">{stars}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
