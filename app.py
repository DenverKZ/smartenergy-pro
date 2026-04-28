import streamlit as st
from utils.theme import init_theme, get_theme_colors, get_css, theme_selector
from utils.api import get_exchange_rates
from utils.data_manager import init_data
import pages.home as home
import pages.settings as settings

st.set_page_config(page_title="SmartEnergy Pro", page_icon="⚡", layout="wide")

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
     page = st.radio("📋 Меню", ["🏠 Главная", "🌤️ Погода", "📅 Календарь", "⚙️ Настройки"], label_visibility="collapsed")
    st.markdown("---")
    st.caption("v.3.4.2 (Stable Edition)")
    st.caption("© 2026 SmartEnergy Systems")

if page == "🏠 Главная":
    home.show()
elif page == "🌤️ Погода":
    import pages.weather as weather
    weather.show()
elif page == "📅 Календарь":
    import pages.calendar as calendar
    calendar.show()
elif page == "⚙️ Настройки":
    settings.show()

st.markdown('<div class="footer">SmartEnergy Pro — промышленная платформа энергомониторинга</div>', unsafe_allow_html=True)
