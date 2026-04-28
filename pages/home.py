import streamlit as st
from datetime import datetime
from utils.api import get_weather

def show():
    st.title("⚡ SmartEnergyPro")
    st.markdown(f"### Система мониторинга на {datetime.now().strftime('%d.%m.%Y')}")
    
    st.markdown("""
    <div class="description-text">
        Добро пожаловать в панель управления SmartEnergyPro. Система обеспечивает непрерывный контроль 
        потребления топливно-энергетических ресурсов (ТЭР) на промышленных объектах.
    </div>
    """, unsafe_allow_html=True)
    
    active_resources = sum(1 for r in st.session_state.resources if r["active"])
    total_resources = len(st.session_state.resources)
    active_tags = len(st.session_state.tags)
    
    weather_data = get_weather()
    valid_temps = [w["temp"] for w in weather_data if w["temp"] is not None]
    avg_temp = sum(valid_temps) / len(valid_temps) if valid_temps else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Ресурсов в базе", f"{active_resources} / {total_resources}")
    col2.metric("Активных ТЭГов", active_tags)
    col3.metric("Городов мониторинга", 5)
    col4.metric("Средняя температура", f"{avg_temp:.1f}°C")
    
    if weather_data:
        st.subheader("🌡️ Текущая температура")
        cols = st.columns(5)
        for idx, w in enumerate(weather_data):
            with cols[idx]:
                st.metric(w["city"], f"{w['temp']:.1f}°C")
