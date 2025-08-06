import streamlit as st

def render_skills_dashboard(skills_data):
    categories = skills_data.get("categories", [])
    if not categories:
        st.info("No skills data available.")
        return

    # Choose display mode
    display_mode = st.radio(
        label="**Display mode:**",
        options=["Stars", "Text", "Bars"],
        horizontal=True
    )
    category_names = [cat["name"] for cat in categories]
    num_cols = 3
    cols = st.columns(num_cols)

    selected_category = None
    for i, category_name in enumerate(category_names):
        col = cols[i % num_cols]
        if col.button(category_name):
            selected_category = category_name

    if "selected_category" not in st.session_state:
        st.session_state.selected_category = category_names[0]
    if selected_category is not None:
        st.session_state.selected_category = selected_category

    category = next(cat for cat in categories if cat["name"] == st.session_state.selected_category)
    sorted_skills = sorted(category["skills"], key=lambda s: s.get("level", 0), reverse=True)

    st.write(f"### {st.session_state.selected_category}")
    for skill in sorted_skills:
        render_skill_row(skill, display_mode)


def render_skill_row(skill, display_mode="Stars"):
    name = skill.get("name", "Unnamed Skill")
    level = skill.get("level", 0)
    exp = skill.get("experience_years", "?")

    # Text label mapping
    level_map = [
        ("Novice", {"max": 1, "color": "#9ca3af"}),         # gray-400
        ("Beginner", {"max": 3, "color": "#fcd34d"}),       # amber-300
        ("Intermediate", {"max": 6, "color": "#60a5fa"}),   # blue-400
        ("Advanced", {"max": 8, "color": "#34d399"}),       # green-400
        ("Expert", {"max": 10, "color": "#a78bfa"})         # purple-400
    ]


    # Determine level label
    for label, meta in level_map:
        if level <= meta["max"]:
            level_text = label
            badge_color = meta["color"]
            break
    else:
        level_text = "Unknown"
        badge_color = "#ccc"

    if display_mode == "Stars":
        stars_html = ''.join([
            f'<span style="font-size: 1.1em; color: gold;">⭐</span>' if i < level
            else f'<span style="font-size: 1.1em; color: #999;">☆</span>'
            for i in range(10)
        ])
        detail_html = f"{stars_html}"
    elif display_mode == "Bars":
        bar_width = int((level / 10) * 100)
        detail_html = f"""
            <div style="width: 100px; height: 12px; background-color: #e5e7eb; border-radius: 6px; overflow: hidden;">
                <div style="width: {bar_width}%; height: 100%; background-color: {badge_color}; transition: width 0.3s;"></div>
            </div>
        """
    else:
        detail_html = f"""
            <span style="
                background-color: {badge_color}33; 
                color: {badge_color}; 
                padding: 4px 10px; 
                font-size: 0.85em; 
                font-weight: 600; 
                border-radius: 999px;
            ">
                {level_text}
            </span>
        """

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
            <div>{detail_html}</div>
            <div style="text-align: right;">
                <strong style="font-size: 0.95em;">{name}</strong><br>
                <span style="font-size: 0.8em; color: gray;">{exp} years</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def get_compact_skill_summary(skills_data):
    lines = []
    for category in skills_data.get("categories", []):
        lines.append(f"{category['name']}:")
        for skill in category["skills"]:
            name = skill["name"]
            level = skill.get("level", "?")
            lines.append(f"  - {name} (Lv {level}/10)")
        lines.append("")  # blank line between categories
    return "\n".join(lines)
