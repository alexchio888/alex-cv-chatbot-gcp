import streamlit as st

def render_skills_dashboard(skills_data):
    categories = skills_data.get("categories", [])
    if not categories:
        st.info("No skills data available.")
        return

    category_names = [cat["name"] for cat in categories]

    # Use session state to remember selection across reruns
    if "selected_category" not in st.session_state:
        st.session_state.selected_category = category_names[0]

    # Render horizontal category selector
    cols = st.columns(len(category_names))
    for idx, cat in enumerate(category_names):
        is_selected = (cat == st.session_state.selected_category)
        button_style = """
            background-color: #4A90E2; 
            color: white; 
            font-weight: bold;
            border-radius: 20px;
            padding: 8px 20px;
            border: none;
            cursor: pointer;
            """ if is_selected else """
            background-color: #eee;
            color: #444;
            border-radius: 20px;
            padding: 8px 20px;
            border: none;
            cursor: pointer;
            """

        with cols[idx]:
            if st.button(cat, key=f"cat_{cat}", help=f"Select {cat}", 
                         args=None, kwargs=None):
                st.session_state.selected_category = cat
            # Hack: Use markdown with button styling instead of real button to style better
            st.markdown(f'<div style="{button_style}; text-align:center;">{cat}</div>', unsafe_allow_html=True)

    # Find selected category data and show skills sorted by level desc
    category = next(cat for cat in categories if cat["name"] == st.session_state.selected_category)
    sorted_skills = sorted(category["skills"], key=lambda s: s.get("level", 0), reverse=True)

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
