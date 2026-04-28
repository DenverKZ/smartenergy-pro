import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.api import get_weather

def show():
    st.title("📊 Аналитика потребления")
    st.caption("Динамика ТЭР, выбросы CO₂ и стоимостные показатели")
    
    # Инициализация данных
    if 'consumption_records' not in st.session_state:
        st.session_state.consumption_records = []
    
    if 'resources' not in st.session_state:
        st.session_state.resources = []
    
    # ========== ПЕРИОД АНАЛИЗА ==========
    st.subheader("📅 Период анализа")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        preset = st.selectbox(
            "Быстрый выбор",
            ["Последние 7 дней", "Последние 30 дней", "Последние 90 дней", "Весь период", "Произвольный"]
        )
    
    today = datetime.now().date()
    
    if preset == "Последние 7 дней":
        start_date = today - timedelta(days=7)
        end_date = today
    elif preset == "Последние 30 дней":
        start_date = today - timedelta(days=30)
        end_date = today
    elif preset == "Последние 90 дней":
        start_date = today - timedelta(days=90)
        end_date = today
    elif preset == "Весь период":
        start_date = date(2024, 1, 1)
        end_date = today
    else:
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Дата от", today - timedelta(days=30))
        with col2:
            end_date = st.date_input("Дата до", today)
    
    st.markdown("---")
    
    # ========== ПОДГОТОВКА ДАННЫХ ==========
    if st.session_state.consumption_records:
        df = pd.DataFrame(st.session_state.consumption_records)
        df['date'] = pd.to_datetime(df['date'])
        
        # Фильтрация по дате
        mask = (df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)
        df_filtered = df[mask].copy()
        
        if not df_filtered.empty:
            # Расчёт показателей
            df_filtered['tut'] = df_filtered['quantity'] * df_filtered['coefTUT']
            df_filtered['co2'] = df_filtered['quantity'] * df_filtered['coefCO2']
            df_filtered['cost'] = df_filtered['quantity'] * df_filtered['tariff']
            
            # ========== ОБЩИЕ МЕТРИКИ ==========
            st.subheader("📈 Итоговые показатели за период")
            
            total_tut = df_filtered['tut'].sum()
            total_co2 = df_filtered['co2'].sum()
            total_cost = df_filtered['cost'].sum()
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📊 Всего записей", len(df_filtered))
            with col2:
                st.metric("⛽ Суммарно т.у.т.", f"{total_tut:.2f}")
            with col3:
                st.metric("🌍 Суммарно CO₂, т", f"{total_co2:.2f}")
            with col4:
                st.metric("💰 Общая стоимость", f"{total_cost:,.0f} ₸")
            
            st.markdown("---")
            
            # ========== ГРАФИК ДИНАМИКИ ==========
            st.subheader("📉 Динамика потребления")
            
            # Группировка по датам
            daily = df_filtered.groupby(df_filtered['date'].dt.date).agg({
                'tut': 'sum',
                'co2': 'sum',
                'cost': 'sum'
            }).reset_index()
            daily.columns = ['date', 'tut', 'co2', 'cost']
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=daily['date'],
                y=daily['tut'],
                name='т.у.т.',
                line=dict(color='#00e5ff', width=2),
                fill='tozeroy',
                fillcolor='rgba(0, 229, 255, 0.1)'
            ))
            
            fig.add_trace(go.Scatter(
                x=daily['date'],
                y=daily['co2'],
                name='т CO₂',
                line=dict(color='#ff9d00', width=2),
                yaxis='y2'
            ))
            
            fig.update_layout(
                title="Ежедневная динамика потребления",
                xaxis_title="Дата",
                yaxis_title="т.у.т.",
                yaxis2=dict(title="т CO₂", overlaying='y', side='right'),
                template='plotly_dark',
                height=450,
                hovermode='x unified',
                plot_bgcolor='#1a1c23',
                paper_bgcolor='#1a1c23'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # ========== СТОИМОСТНАЯ ДИНАМИКА ==========
            st.subheader("💰 Динамика стоимости")
            
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                x=daily['date'],
                y=daily['cost'],
                name='Стоимость, ₸',
                marker_color='#00e5ff',
                marker_line_color='#00b8d4',
                marker_line_width=1
            ))
            
            fig2.update_layout(
                title="Ежедневные затраты",
                xaxis_title="Дата",
                yaxis_title="Стоимость, тенге",
                template='plotly_dark',
                height=400,
                plot_bgcolor='#1a1c23',
                paper_bgcolor='#1a1c23'
            )
            
            st.plotly_chart(fig2, use_container_width=True)
            
            # ========== РАСПРЕДЕЛЕНИЕ ПО РЕСУРСАМ ==========
            st.subheader("🥧 Распределение по видам ресурсов")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Топ ресурсов по т.у.т.
                resource_tut = df_filtered.groupby('resource')['tut'].sum().sort_values(ascending=False).head(8)
                
                fig3 = px.pie(
                    values=resource_tut.values,
                    names=resource_tut.index,
                    title="Распределение по т.у.т.",
                    color_discrete_sequence=px.colors.sequential.Tealgrn
                )
                fig3.update_layout(template='plotly_dark', paper_bgcolor='#1a1c23')
                st.plotly_chart(fig3, use_container_width=True)
            
            with col2:
                # Топ ресурсов по стоимости
                resource_cost = df_filtered.groupby('resource')['cost'].sum().sort_values(ascending=False).head(8)
                
                fig4 = px.bar(
                    x=resource_cost.values,
                    y=resource_cost.index,
                    orientation='h',
                    title="Затраты по видам ресурсов, ₸",
                    color=resource_cost.values,
                    color_continuous_scale='Tealgrn'
                )
                fig4.update_layout(template='plotly_dark', paper_bgcolor='#1a1c23', height=400)
                st.plotly_chart(fig4, use_container_width=True)
            
            # ========== РАСПРЕДЕЛЕНИЕ ПО ТЕГАМ ==========
            if 'tag' in df_filtered.columns:
                st.subheader("🏷️ Распределение по тегам")
                
                tag_data = df_filtered.groupby('tag').agg({
                    'tut': 'sum',
                    'cost': 'sum'
                }).reset_index()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig5 = px.pie(
                        tag_data,
                        values='tut',
                        names='tag',
                        title="Распределение т.у.т. по тегам",
                        color_discrete_sequence=px.colors.sequential.Teal
                    )
                    fig5.update_layout(template='plotly_dark', paper_bgcolor='#1a1c23')
                    st.plotly_chart(fig5, use_container_width=True)
                
                with col2:
                    fig6 = px.bar(
                        tag_data,
                        x='tag',
                        y='cost',
                        title="Затраты по тегам, ₸",
                        color='cost',
                        color_continuous_scale='Tealgrn'
                    )
                    fig6.update_layout(template='plotly_dark', paper_bgcolor='#1a1c23')
                    st.plotly_chart(fig6, use_container_width=True)
            
            # ========== СВОДНАЯ ТАБЛИЦА ==========
            with st.expander("📋 Детализация по ресурсам"):
                summary = df_filtered.groupby('resource').agg({
                    'quantity': 'sum',
                    'tut': 'sum',
                    'co2': 'sum',
                    'cost': 'sum'
                }).round(2).reset_index()
                summary.columns = ['Ресурс', 'Кол-во', 'т.у.т.', 'т CO₂', 'Стоимость, ₸']
                st.dataframe(summary, use_container_width=True)
                
                # Экспорт
                csv = summary.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    "📥 Экспорт отчёта в CSV",
                    csv,
                    f"analytics_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv"
                )
            
            # ========== КОРРЕЛЯЦИЯ С ПОГОДОЙ ==========
            with st.expander("🌡️ Корреляция с температурой"):
                st.caption("Анализ влияния погодных условий на потребление")
                
                weather_data = get_weather()
                if weather_data and not daily.empty:
                    # Берём первый город для анализа
                    avg_temp = sum(w['temp'] for w in weather_data if w['temp'] is not None) / len([w for w in weather_data if w['temp'] is not None])
                    st.metric("Средняя температура за период", f"{avg_temp:.1f}°C")
                    
                    st.info("""
                    **📌 Анализ влияния температуры на потребление:**
                    
                    При понижении температуры обычно растёт потребление:
                    - Отопление помещений
                    - Подогрев технологических сред
                    - Увеличение времени работы оборудования
                    
                    *Для точного анализа рекомендуется накопить больше исторических данных.*
                    """)
        
        else:
            st.warning("⚠️ Нет данных за выбранный период. Добавьте записи потребления на странице «Ввод данных».")
    
    else:
        st.info("📭 Нет данных для анализа. Перейдите на страницу «Ввод данных» и добавьте первые записи потребления.")
    
    # ========== ВЫВОД ПО ТЭГАМ ==========
    st.markdown("---")
    st.caption("Аналитика обновляется автоматически при добавлении новых записей потребления")
