import streamlit as st

def init_theme():
    if 'theme' not in st.session_state:
        st.session_state.theme = "dark"
    query_params = st.query_params
    if 'theme' in query_params:
        st.session_state.theme = query_params['theme']

def get_theme_colors():
    themes = {
        "light": {
            "bg": "#ffffff", "bg_secondary": "#f3f4f6",
            "text": "#111827", "text_secondary": "#6b7280",
            "border": "#e5e7eb", "accent": "#0d9488", "accent_light": "#14b8a6",
            "card_bg": "#ffffff", "card_border": "#e5e7eb",
        },
        "dark": {
            "bg": "#0f1117", "bg_secondary": "#1a1c23",
            "text": "#e1e4e8", "text_secondary": "#8a8d98",
            "border": "#2a2c33", "accent": "#00e5ff", "accent_light": "#00b8d4",
            "card_bg": "#1a1c23", "card_border": "#2a2c33",
        }
    }
    return themes.get(st.session_state.theme, themes["dark"])

def get_css(colors):
    return f"""
    <style>
        .stApp {{ background-color: {colors["bg"]}; }}
        h1, h2, h3 {{ color: {colors["text"]} !important; }}
        .description-text {{
            border-left: 3px solid {colors["accent"]};
            padding-left: 1rem;
            margin: 1rem 0;
            color: {colors["text_secondary"]};
        }}
        .metric-card {{
            background-color: {colors["card_bg"]};
            border: 1px solid {colors["card_border"]};
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
        }}
        .metric-value {{
            font-size: 1.8rem;
            font-weight: bold;
            color: {colors["accent"]};
        }}
        .metric-label {{
            font-size: 0.7rem;
            color: {colors["text_secondary"]};
            text-transform: uppercase;
        }}
        [data-testid="stSidebar"] {{
            background-color: {colors["bg_secondary"]};
            border-right: 1px solid {colors["border"]};
        }}
        .stButton button {{
            background-color: {colors["accent"]};
            color: {colors["bg"]};
        }}
        .footer {{
            text-align: center;
            padding: 1rem;
            color: {colors["text_secondary"]};
            font-size: 0.7rem;
            border-top: 1px solid {colors["border"]};
            margin-top: 2rem;
        }}
    </style>
    """

def theme_selector():
    st.markdown("**🎨 Тема оформления**")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🌞 Светлая", use_container_width=True, key="theme_light"):
            st.query_params["theme"] = "light"
            st.rerun()
    with col2:
        if st.button("🌙 Тёмная", use_container_width=True, key="theme_dark"):
            st.query_params["theme"] = "dark"
            st.rerun()
    with col3:
        if st.button("💻 Системная", use_container_width=True, key="theme_system"):
            st.query_params["theme"] = "system"
            st.rerun()
