import streamlit as st

def init_theme():
    """Загружает сохранённую тему из параметров URL"""
    if 'theme' not in st.session_state:
        st.session_state.theme = "dark"
    query_params = st.query_params
    if 'theme' in query_params:
        st.session_state.theme = query_params['theme']

def get_theme_colors():
    """Возвращает цвета для текущей темы (светлая/тёмная)"""
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
    """Генерирует CSS код на основе выбранной темы"""
    return f"""
    <style>
        /* Основной фон */
        .stApp {{ background-color: {colors["bg"]}; }}
        
        /* Заголовки */
        h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
            color: {colors["text"]} !important;
        }}
        
        /* Текст */
        .stMarkdown, .stMetric label, .stMetric value {{
            color: {colors["text"]};
        }}
        
        /* Карточки метрик */
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
        
        /* Боковая панель */
        [data-testid="stSidebar"] {{
            background-color: {colors["bg_secondary"]};
            border-right: 1px solid {colors["border"]};
        }}
        
        /* Стиль для кнопок темы (иконки) */
        .theme-icon {{
            background: none;
            border: none;
            font-size: 24px;
            cursor: pointer;
            padding: 8px;
            border-radius: 8px;
            transition: all 0.2s;
        }}
        .theme-icon:hover {{
            background-color: {colors["border"]};
            transform: scale(1.1);
        }}
        
        /* Кнопки */
        .stButton button {{
            background-color: {colors["accent"]};
            color: {colors["bg"]};
            font-weight: 600;
            border: none;
        }}
        .stButton button:hover {{
            background-color: {colors["accent_light"]};
            transform: translateY(-1px);
        }}
        
        /* Разделитель */
        hr {{ border-color: {colors["border"]}; margin: 1rem 0; }}
        
        /* Футер */
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
    """Отображает три иконки для выбора темы (светлая/тёмная/системная)"""
    
    # Три колонки для иконок
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Кнопка "Светлая тема" (только иконка)
        if st.button("🌞", key="theme_light", use_container_width=True, help="Светлая тема"):
            st.query_params["theme"] = "light"
            st.rerun()
    
    with col2:
        # Кнопка "Тёмная тема" (только иконка)
        if st.button("🌙", key="theme_dark", use_container_width=True, help="Тёмная тема"):
            st.query_params["theme"] = "dark"
            st.rerun()
    
    with col3:
        # Кнопка "Системная тема" (только иконка)
        if st.button("💻", key="theme_system", use_container_width=True, help="Системная тема"):
            st.query_params["theme"] = "system"
            st.rerun()
