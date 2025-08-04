import streamlit as st

def render_skills_dashboard(skills_data):
    categories = skills_data.get("categories", [])
    if not categories:
        st.info("No skills data available.")
        return

    category_names = [cat["name"] for cat in categories]

    # Number of columns to split the categories into
    num_cols = 3  
    cols = st.columns(num_cols)

    # Flatten buttons into columns in round-robin fashion
    selected_category = None
    for i, category_name in enumerate(category_names):
        col = cols[i % num_cols]
        if col.button(category_name):
            selected_category = category_name

    # Remember previously selected category (session state) or default to first
    if "selected_category" not in st.session_state:
        st.session_state.selected_category = category_names[0]

    if selected_category is not None:
        st.session_state.selected_category = selected_category

    # Use the selected category to render skills
    category = next(cat for cat in categories if cat["name"] == st.session_state.selected_category)
    sorted_skills = sorted(category["skills"], key=lambda s: s.get("level", 0), reverse=True)

    st.write(f"### {st.session_state.selected_category}")
    for skill in sorted_skills:
        render_skill_row(skill)


def render_skill_row(skill):
    name = skill.get("name", "Unnamed Skill")
    level = skill.get("level", 0)
    exp = skill.get("experience_years", "?")

    stars_html = ''.join([
        f'<span style="font-size: 1.1em; color: gold;">⭐</span>' if i < level
        else f'<span style="font-size: 1.1em; color: #999;">☆</span>'
        for i in range(10)
    ])

    st.markdown(
        f"""
        <div style="
            background-color: rgba(240, 240, 240, 0.05); 
            padding: 12px 16px; 
            margin-bottom: 10px; 
            border-radius: 10px; 
            border: 1px solid rgba(200, 200, 200, 0.15); 
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            display: flex; 
            justify-content: space-between; 
            align-items: center;
        ">
            <div>{stars_html}</div>
            <div style="text-align: right;">
                <strong style="font-size: 0.95em;">{name}</strong><br>
                <span style="font-size: 0.8em; color: gray;">{exp} years</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
