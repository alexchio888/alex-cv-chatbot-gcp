import streamlit as st

def render_sidebar(st_session_state, generate_chat_text, generate_chat_json, generate_chat_markdown, reset_conversation):
    tab_contact, tab_prompts, tab_download, tab_settings = st.sidebar.tabs(
        ["📇 Contact", "💡 Try Asking", "💬 Download Chat", "⚙️ Settings"]
    )

    with tab_contact:
        st.markdown("## 👤 Alexandros Chionidis")
        
        # Location
        maps_url = "https://www.google.com/maps/place/Melissia,+Athens,+Greece"
        st.markdown(
            f'<p style="margin: 0;"><a href="{maps_url}" target="_blank" style="text-decoration:none;">'
            f'🏠 <strong>Melissia, Athens, Greece</strong></a></p>',
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # Contact Links
        contact_links = [
            {
                "label": "LinkedIn",
                "icon": "https://cdn-icons-png.flaticon.com/512/174/174857.png",
                "url": "https://www.linkedin.com/in/alexandros-chionidis-51579421b/",
            },
            {
                "label": "GitHub",
                "icon": "https://cdn-icons-png.flaticon.com/512/733/733553.png",
                "url": "https://github.com/alexchio888",
            },
            {
                "label": "Email",
                "icon": "https://cdn-icons-png.flaticon.com/512/732/732200.png",
                "url": "mailto:alexandroschio@gmail.com",
            },
        ]

        for contact in contact_links:
            st.markdown(
                f'<a href="{contact["url"]}" target="_blank" style="text-decoration:none; display: flex; align-items: center; margin: 4px 0;">'
                f'<img src="{contact["icon"]}" width="20" style="margin-right:8px;" /> {contact["label"]}</a>',
                unsafe_allow_html=True,
            )

        st.markdown("---")

        # Download CV
        cv_html = """<a href="https://github.com/alexchio888/cv-chatbot/raw/main/docs/Alexandros_Chionidis_CV.pdf" target="_blank" style="text-decoration:none; display: flex; align-items: center;">
            <img src="https://cdn-icons-png.flaticon.com/512/337/337946.png" width="20" style="margin-right:8px;" /> Download CV
        </a>"""
        st.markdown(cv_html, unsafe_allow_html=True)


    with tab_prompts:
        st.markdown("### 💡 Try asking about:")
        categories = {
            "Education": ["Where did you study?", "Tell me about your academic background."],
            "Work Experience": ["What was your role at Intrasoft?", "Describe your work at Waymore.", "What projects did you do in retail before tech?"],
            "Skills & Tools": ["What technologies are you proficient with?", "How do you use Spark and Kafka in your work?", "Tell me about your experience with GCP."],
            "Certifications": ["Do you have any certifications?", "Are you planning to get any certifications soon?"],
            "Projects": ["Can you describe a key data engineering project?", "What was your biggest technical challenge?"],
        }

        for category, prompts in categories.items():
            with st.expander(category, expanded=False):
                for prompt in prompts:
                    if st.button(prompt, key=prompt):
                        st.session_state.messages.append({"role": "user", "content": prompt})

    with tab_download:
        st.markdown("### 📥 Download Chat History")
        if "messages" in st_session_state and st_session_state.messages:
            chat_txt = generate_chat_text()
            chat_json = generate_chat_json()
            chat_md = generate_chat_markdown()

            st.download_button(
                label="📄 Download as TXT",
                data=chat_txt,
                file_name="alexandros_clone_chat.txt",
                mime="text/plain",
            )
            st.download_button(
                label="🧾 Download as JSON",
                data=chat_json,
                file_name="alexandros_clone_chat.json",
                mime="application/json",
            )
            st.download_button(
                label="📝 Download as Markdown",
                data=chat_md,
                file_name="alexandros_clone_chat.md",
                mime="text/markdown",
            )
        else:
            st.info("No chat history to download yet.")

    with tab_settings:
        st.markdown("### ⚙️ Chat Settings")
        model = st.selectbox(
            "Change chatbot model:",
            [
                "mistral-large",
                "reka-flash",
                "llama2-70b-chat",
                "gemma-7b",
                "mixtral-8x7b",
                "mistral-7b",
            ],
            index=0,
        )

        embedding_size = st.selectbox(
            "Select embedding dimension:",
            ["1024", "768"],
            index=0,
            format_func=lambda x: f"{x}-dim embedding",
        )

        if st.button("Reset Chat"):
            reset_conversation()
