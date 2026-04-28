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

st.set_page_config(page_title="SmartEnergyPro", page_icon="⚡", layout="wide")

init_theme()
init_data()
colors = get_theme_colors()
st.markdown(get_css(colors), unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## ⚡ SmartEnergyPro")
    st.markdown("---")
    theme_selector()
    st.markdown("---")
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
    page = st.radio("📋 Меню", ["🏠 Главная", "📊 Аналитика", "🌤️ Погода", "📅 Календарь", "⚙️ Настройки", "🆘 Поддержка"], label_visibility="collapsed")
    st.markdown("---")
    st.markdown("<p style='text-align: center; color: gray; font-size: 12px;'>Версия 3.4.2 | SmartEnergyPro © 2026</p>", unsafe_allow_html=True)

if page == "🏠 Главная":
    home.show()
elif page == "📊 Аналитика":
    analytics.show()
elif page == "🌤️ Погода":
    weather.show()
elif page == "📅 Календарь":
    calendar.show()
elif page == "⚙️ Настройки":
    settings.show()
elif page == "🆘 Поддержка":
    support.show()
