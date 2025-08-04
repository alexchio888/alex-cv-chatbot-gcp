import streamlit as st

def render_sidebar(
    st_session_state,
    generate_chat_text=None,
    generate_chat_json=None,
    generate_chat_markdown=None,
    show_tabs=True,  # controls whether to show tabs below contact
):
    # Always render contact info at top
    _render_contact()

    if show_tabs:
        tab_prompts, tab_download, tab_settings = st.sidebar.tabs(
            ["💡 Try Asking", "💬 Export Chat", "⚙️ Settings"]
        )
        with tab_prompts:
            _render_prompts(st_session_state)
        with tab_download:
            _render_download(st_session_state, generate_chat_text, generate_chat_json, generate_chat_markdown)
        with tab_settings:
            _render_settings(st_session_state)

    # --- FOOTER ---
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        '<p style="font-size: 0.8em; color: gray;">Made by Alexandros • <a href="https://github.com/alexchio888" target="_blank">GitHub</a></p>',
        unsafe_allow_html=True
    )


def _render_contact():
    st.sidebar.markdown("## 👤 Alexandros Chionidis")

    # Location
    maps_url = "https://www.google.com/maps/place/Melissia,+Athens,+Greece"
    st.sidebar.markdown(
        f'<p style="margin: 0 0 10px 0;">'
        f'🏠 <a href="{maps_url}" target="_blank" style="text-decoration:none; color: inherit;">Melissia, Athens, Greece</a></p>',
        unsafe_allow_html=True,
    )

    # Phone number (added)
    phone_number = "+30 6933419882"  # Replace with your actual number
    phone_icon = "https://cdn-icons-png.flaticon.com/512/724/724664.png"
    st.sidebar.markdown(
        f'<p style="margin: 0 0 10px 0; display: flex; align-items: center;">'
        f'<img src="{phone_icon}" width="20" style="margin-right:8px;" /> {phone_number}</p>',
        unsafe_allow_html=True,
    )

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
        st.sidebar.markdown(
            f'<a href="{contact["url"]}" target="_blank" style="text-decoration:none; display: flex; align-items: center; margin: 4px 0;">'
            f'<img src="{contact["icon"]}" width="20" style="margin-right:8px;" /> {contact["label"]}</a>',
            unsafe_allow_html=True,
        )

    # Download CV link
    cv_html = """
    <a href="https://github.com/alexchio888/cv-chatbot/raw/main/docs/Alexandros_Chionidis_CV.pdf" target="_blank" 
       style="text-decoration:none; display: flex; align-items: center;">
        <img src="https://cdn-icons-png.flaticon.com/512/337/337946.png" width="20" style="margin-right:8px;" /> Download CV
    </a>"""
    st.sidebar.markdown(cv_html, unsafe_allow_html=True)


def _render_prompts(st_session_state):
    st.markdown("### 💡 Try asking about:")
    categories = {
        "Education": ["Where did you study?", "Tell me about your academic background."],
        "Work Experience": ["What was your role at Netcompany - Intrasoft?", "Describe your work at Waymore.", "What is your work experience besides tech?"],
        "Skills & Tools": ["What technologies are you proficient with?", "How do you use Spark and Kafka in your work?", "Tell me about your experience with GCP."],
        "Certifications": ["Do you have any certifications?", "Are you planning to get any certifications soon?"],
        "Projects": ["Can you describe a key data engineering project?", "What was your biggest technical challenge?"],
    }

    for category, prompts in categories.items():
        with st.expander(category, expanded=False):
            for prompt in prompts:
                if st.button(prompt, key=prompt):
                    st.session_state.messages.append({"role": "user", "content": prompt})


def _render_download(st_session_state, generate_chat_text, generate_chat_json, generate_chat_markdown):
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


def _render_settings(st_session_state):
    st.markdown("### ⚙️ Chat Settings")
    st.markdown("_For experimentation and dev purposes_")

    st.session_state.model = st.selectbox(
        "Change chatbot model:",
        [
            "mistral-large",
            "reka-flash",
            "llama2-70b-chat",
            "gemma-7b",
            "mixtral-8x7b",
            "mistral-7b",
        ],
        index=["mistral-large", "reka-flash", "llama2-70b-chat", "gemma-7b", "mixtral-8x7b", "mistral-7b"].index(st.session_state.get("model", "mistral-large")),
    )

    st.session_state.embedding_size = st.selectbox(
        "Select embedding dimension:",
        ["1024", "768"],
        index=["1024", "768"].index(st.session_state.get("embedding_size", "1024")),
        format_func=lambda x: f"{x}-dim embedding",
    )

    st.divider()

    st.markdown("### ⚙️ Chat Context Settings")

    st.session_state.include_history = st.checkbox(
        "Include previous messages in prompt context",
        value=st.session_state.get("include_history", True),
        help="Add previous chat messages to the prompt context for better understanding."
    )

    st.session_state.context_message_count = st.number_input(
        "Number of previous messages to include",
        min_value=0,
        max_value=10,
        value=st.session_state.get("context_message_count", 4),
        step=2,
        help="How many previous messages to include in the prompt context."
    )
