import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.api import get_weather

def show():
    st.title("🌤️ Метеорологический архив")
    st.caption("Текущие условия, исторические данные и ручные замеры")
    
    # ========== ТЕКУЩАЯ ПОГОДА ==========
    st.subheader("📍 Текущая температура по городам")
    
    weather_data = get_weather()
    if weather_data:
        cols = st.columns(5)
        for idx, w in enumerate(weather_data):
            with cols[idx]:
                temp_display = f"{w['temp']:.1f}°C" if w['temp'] is not None else "—"
                st.metric(w["city"], temp_display)
    
    st.markdown("---")
    
    # ========== РУЧНОЙ ЖУРНАЛ ЗАМЕРОВ ==========
    st.subheader("📝 Ручной журнал замеров")
    st.caption("Добавляйте собственные показания температуры и влажности")
    
    # Инициализация журнала, если его нет
    if 'weather_log' not in st.session_state:
        st.session_state.weather_log = []
    
    col1, col2, col3 = st.columns(3)
    with col1:
        manual_temp = st.number_input("🌡️ Температура, °C", value=15.0, step=0.5, format="%.1f")
    with col2:
        manual_hum = st.number_input("💧 Влажность, %", min_value=0, max_value=100, value=50)
    with col3:
        if st.button("💾 Записать замер", type="primary", use_container_width=True):
            new_log = {
                "id": str(datetime.now().timestamp()),
                "timestamp": datetime.now().isoformat(),
                "temperature": manual_temp,
                "humidity": manual_hum
            }
            st.session_state.weather_log.append(new_log)
            st.success("✅ Запись добавлена")
            st.rerun()
    
    # ========== ГРАФИК ЗАМЕРОВ ==========
    if st.session_state.weather_log:
        df_log = pd.DataFrame(st.session_state.weather_log)
        df_log['timestamp'] = pd.to_datetime(df_log['timestamp'])
        df_log = df_log.sort_values('timestamp')
        
        # Берём последние 20 записей для графика
        df_log_recent = df_log.tail(20)
        
        fig = go.Figure()
        
        # График температуры
        fig.add_trace(go.Scatter(
            x=df_log_recent['timestamp'],
            y=df_log_recent['temperature'],
            name='Температура, °C',
            line=dict(color='#00e5ff', width=2),
            mode='lines+markers',
            marker=dict(size=8)
        ))
        
        # График влажности
        fig.add_trace(go.Scatter(
            x=df_log_recent['timestamp'],
            y=df_log_recent['humidity'],
            name='Влажность, %',
            line=dict(color='#ff9d00', width=2),
            mode='lines+markers',
            marker=dict(size=8),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title="Динамика замеров",
            xaxis_title="Дата/Время",
            yaxis_title="Температура, °C",
            yaxis2=dict(title="Влажность, %", overlaying='y', side='right'),
            template='plotly_dark',
            height=400,
            hovermode='x unified',
            plot_bgcolor='#1a1c23',
            paper_bgcolor='#1a1c23',
            font=dict(color='#e1e4e8')
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # ========== ТАБЛИЦА ЗАМЕРОВ ==========
        with st.expander("📋 История всех замеров"):
            display_log = df_log[['timestamp', 'temperature', 'humidity']].copy()
            display_log.columns = ['Дата/Время', 'Температура, °C', 'Влажность, %']
            display_log = display_log.sort_values('Дата/Время', ascending=False)
            st.dataframe(display_log, use_container_width=True)
            
            # Кнопка очистки журнала
            if st.button("🗑️ Очистить весь журнал", type="secondary"):
                st.session_state.weather_log = []
                st.rerun()
    else:
        st.info("📊 Журнал замеров пуст. Добавьте первый замер с помощью формы выше.")
    
    st.markdown("---")
    
    # ========== ИНФОРМАЦИЯ О ПОГОДЕ ==========
    with st.expander("ℹ️ О данных погоды"):
        st.markdown("""
        **Источник данных:** Open-Meteo API  
        **Обновление:** Автоматически при загрузке страницы  
        **Города мониторинга:** Атырау, Актау, Кульсары, Уральск, Актобе  
        
        Ручной журнал позволяет фиксировать:
        - 📍 Точечные замеры на объектах
        - 🔧 Показания локальных метеостанций
        - 📝 Наблюдения персонала
        """)
