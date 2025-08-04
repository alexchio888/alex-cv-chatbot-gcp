import streamlit as st

def render_skills_dashboard(skills_data):
    st.subheader("🧠 Skills Overview")

    categories = skills_data.get("categories", [])
    if not categories:
        st.info("No skills data available.")
        return

    for category in categories:
        # Category card wrapper
        st.markdown(
            f"""
            <div style="
                background-color: rgba(220, 220, 220, 0.1);
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 25px;
                border: 1.5px solid rgba(180, 180, 180, 0.3);
                box-shadow: 0 2px 6px rgba(0,0,0,0.07);
            ">
                <h3 style="
                    border-left: 6px solid #4A90E2;  /* accent color bar */
                    padding-left: 12px;
                    margin-bottom: 18px;
                    font-weight: 700;
                    color: #333;
                ">{category['name']}</h3>
            """,
            unsafe_allow_html=True
        )

        for skill in category["skills"]:
            render_skill_row(skill)

        st.markdown("</div>", unsafe_allow_html=True)

        # Optional separator between categories
        # st.markdown("---")

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
