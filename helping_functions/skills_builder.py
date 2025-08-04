import streamlit as st

def render_category_selector(categories, selected_category):
    # Horizontal scroll container with buttons
    st.markdown(
        """
        <style>
        .scrolling-wrapper {
            overflow-x: auto;
            white-space: nowrap;
            padding-bottom: 10px;
        }
        .tab-button {
            display: inline-block;
            padding: 8px 16px;
            margin-right: 8px;
            border-radius: 20px;
            background-color: #eee;
            cursor: pointer;
            user-select: none;
        }
        .tab-button.selected {
            background-color: #4A90E2;
            color: white;
            font-weight: bold;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    selected_cat = None
    container = st.empty()
    with container.container():
        st.markdown('<div class="scrolling-wrapper">', unsafe_allow_html=True)
        for cat in categories:
            is_selected = (cat == selected_category)
            classes = "tab-button selected" if is_selected else "tab-button"
            if st.button(cat, key=f"cat_{cat}", help=f"Select {cat} category"):
                selected_cat = cat
            st.markdown(f'<span class="{classes}">{cat}</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Return selected category if clicked, else current selection
    return selected_cat or selected_category

def render_skills_dashboard(skills_data):
    categories = skills_data.get("categories", [])
    if not categories:
        st.info("No skills data available.")
        return
    
    category_names = [cat["name"] for cat in categories]
    # Default first category
    selected_category = category_names[0]

    # Stateful storage to remember selection
    if 'selected_category' not in st.session_state:
        st.session_state.selected_category = selected_category

    selected = render_category_selector(category_names, st.session_state.selected_category)
    if selected:
        st.session_state.selected_category = selected

    # Render skills of selected category
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
