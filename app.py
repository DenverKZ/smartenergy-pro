# ============================================================================
# ПОДКЛЮЧЕНИЕ БИБЛИОТЕК И МОДУЛЕЙ
# ============================================================================

import streamlit as st
from utils.theme import init_theme, get_theme_colors, get_css, theme_selector
from utils.api import get_exchange_rates
from utils.data_manager import init_data
import pages.home as home
import pages.settings as settings
import pages.analytics as analytics
import pages.weather as weather
import pages.calendar as calendar
import pages.support as support


# ============================================================================
# НАСТРОЙКА ГЛАВНОГО ОКНА ПРИЛОЖЕНИЯ
# ============================================================================

st.set_page_config(
    page_title="SmartEnergyPro",
    page_icon="⚡",
    layout="wide"
)


# ============================================================================
# ЗАГРУЗКА ТЕМЫ И ДАННЫХ ПРИ ЗАПУСКЕ
# ============================================================================

init_theme()
init_data()
colors = get_theme_colors()
st.markdown(get_css(colors), unsafe_allow_html=True)


# ============================================================================
# БОКОВАЯ ПАНЕЛЬ (SIDEBAR) - ЛЕВОЕ МЕНЮ
# ============================================================================

with st.sidebar:
    
    # ----- ЗАГОЛОВОК -----
    st.markdown("## ⚡ SmartEnergyPro")
    st.markdown("---")
    
    # ----- ВЫБОР ТЕМЫ (СВЕТЛАЯ/ТЁМНАЯ/СИСТЕМНАЯ) -----
    theme_selector()
    st.markdown("---")
    
    # ----- КУРСЫ ВАЛЮТ -----
    st.markdown("**Курсы валют → ₸**")
    rates = get_exchange_rates()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**$1 USD**  \n{rates['USD']} ₸")
        st.markdown(f"**€1 EUR**  \n{rates['EUR']} ₸")
    with col2:
        st.markdown(f"**₽1 RUB**  \n{rates['RUB']} ₸")
        st.markdown(f"**¥1 CNY**  \n{rates['CNY']} ₸")
    st.markdown("---")
    
    # ========== НАВИГАЦИОННЫЕ КНОПКИ В 1 СТОЛБЕЦ ==========
    # Сохраняем выбранную страницу в session_state
    if 'page' not in st.session_state:
        st.session_state.page = "🏠 Главная"
    
    st.markdown("**📋 Меню**")
    
    # Кнопка 1: Главная
    if st.button("🏠 Главная", use_container_width=True):
        st.session_state.page = "🏠 Главная"
        st.rerun()
    
    # Кнопка 2: Аналитика
    if st.button("📊 Аналитика", use_container_width=True):
        st.session_state.page = "📊 Аналитика"
        st.rerun()
    
    # Кнопка 3: Погода
    if st.button("🌤️ Погода", use_container_width=True):
        st.session_state.page = "🌤️ Погода"
        st.rerun()
    
    # Кнопка 4: Календарь
    if st.button("📅 Календарь", use_container_width=True):
        st.session_state.page = "📅 Календарь"
        st.rerun()
    
    # Кнопка 5: Настройки
    if st.button("⚙️ Настройки", use_container_width=True):
        st.session_state.page = "⚙️ Настройки"
        st.rerun()
    
    # Кнопка 6: Поддержка
    if st.button("🆘 Поддержка", use_container_width=True):
        st.session_state.page = "🆘 Поддержка"
        st.rerun()
    
    st.markdown("---")
    
    # ----- ВЕРСИЯ ПРОГРАММЫ В САМОМ НИЗУ ПАНЕЛИ -----
    st.markdown(
        "<p style='text-align: center; color: gray; font-size: 12px;'>Версия 3.4.2 | SmartEnergyPro © 2026</p>",
        unsafe_allow_html=True
    )


# ============================================================================
# НАВИГАЦИЯ ПО СТРАНИЦАМ (ОТОБРАЖЕНИЕ ВЫБРАННОГО КОНТЕНТА)
# ============================================================================

# Получаем выбранную страницу из session_state (по умолчанию "🏠 Главная")
current_page = st.session_state.get("page", "🏠 Главная")

if current_page == "🏠 Главная":
    home.show()
elif current_page == "📊 Аналитика":
    analytics.show()
elif current_page == "🌤️ Погода":
    weather.show()
elif current_page == "📅 Календарь":
    calendar.show()
elif current_page == "⚙️ Настройки":
    settings.show()
elif current_page == "🆘 Поддержка":
    support.show()
