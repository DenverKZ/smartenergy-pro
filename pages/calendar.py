import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import calendar as cal

def show():
    st.title("📅 Календарь событий")
    st.caption("Поверки приборов учёта, ТО, отчётность и плановые мероприятия")
    
    # Инициализация событий
    if 'calendar_events' not in st.session_state:
        # Примеры событий для демонстрации
        st.session_state.calendar_events = [
            {
                "id": "1",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "title": "Поверка счётчика Boiler_01",
                "notes": "Основной котел, требуется допуск",
                "type": "Поверка"
            },
            {
                "id": "2",
                "date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
                "title": "Техническое обслуживание Main_Meter",
                "notes": "Плановое ТО",
                "type": "ТО"
            }
        ]
    
    # ========== ФОРМА ДОБАВЛЕНИЯ СОБЫТИЯ ==========
    with st.expander("➕ Добавить новое событие", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            event_date = st.date_input("Дата", datetime.now())
        with col2:
            event_type = st.selectbox("Тип события", ["Поверка", "ТО", "Отчёт", "Прочее"])
        with col3:
            event_title = st.text_input("Название", placeholder="Поверка счётчика...")
        
        event_notes = st.text_area("Примечание", placeholder="Дополнительная информация (необязательно)", height=80)
        
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        with col4:
            if st.button("💾 Сохранить событие", type="primary", use_container_width=True):
                if event_title:
                    new_event = {
                        "id": str(datetime.now().timestamp()),
                        "date": event_date.strftime("%Y-%m-%d"),
                        "title": event_title,
                        "notes": event_notes,
                        "type": event_type
                    }
                    st.session_state.calendar_events.append(new_event)
                    st.success(f"✅ Событие добавлено: {event_title}")
                    st.rerun()
                else:
                    st.error("❌ Введите название события")
    
    st.markdown("---")
    
    # ========== ОТОБРАЖЕНИЕ КАЛЕНДАРЯ ==========
    # Преобразуем события в DataFrame
    events_df = pd.DataFrame(st.session_state.calendar_events)
    if not events_df.empty:
        events_df['date'] = pd.to_datetime(events_df['date'])
    
    # Текущий месяц для отображения
    today = datetime.now()
    
    # Выбор месяца и года
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        selected_year = st.selectbox("Год", range(today.year - 1, today.year + 3), index=1)
    with col2:
        selected_month = st.selectbox("Месяц", range(1, 13), index=today.month - 1)
    with col3:
        if st.button("📅 Сегодня", use_container_width=True):
            selected_year = today.year
            selected_month = today.month
            st.rerun()
    
    # Получаем календарь месяца
    month_cal = cal.monthcalendar(selected_year, selected_month)
    month_names = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                   "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
    
    st.markdown(f"### {month_names[selected_month - 1]} {selected_year}")
    
    # Цвета для типов событий
    type_colors = {
        "Поверка": "🔵",
        "ТО": "🟠",
        "Отчёт": "🟢",
        "Прочее": "⚪"
    }
    
    # Отображение календарной сетки
    days = ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"]
    cols_header = st.columns(7)
    for i, day in enumerate(days):
        with cols_header[i]:
            st.markdown(f"**{day}**")
    
    # Строки календаря
    for week in month_cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                if day == 0:
                    st.markdown(" ")
                else:
                    current_date = date(selected_year, selected_month, day)
                    date_str = current_date.strftime("%Y-%m-%d")
                    
                    # Находим события на этот день
                    day_events = []
                    if not events_df.empty:
                        day_events = events_df[events_df['date'].dt.date == current_date]
                    
                    # Подсветка сегодняшнего дня
                    is_today = current_date == today.date()
                    
                    if is_today:
                        st.markdown(f"**🔵 {day}**")
                    else:
                        st.markdown(f"**{day}**")
                    
                    # Отображаем события
                    for _, event in day_events.iterrows():
                        emoji = type_colors.get(event['type'], "⚪")
                        st.markdown(f"{emoji} {event['title'][:15]}{'...' if len(event['title']) > 15 else ''}")
    
    st.markdown("---")
    
    # ========== СПИСОК ВСЕХ СОБЫТИЙ ==========
    st.subheader("📋 Все запланированные события")
    
    if events_df.empty:
        st.info("Нет запланированных событий. Добавьте первое событие с помощью формы выше.")
    else:
        # Сортировка по дате
        events_sorted = events_df.sort_values('date')
        
        for _, event in events_sorted.iterrows():
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 4, 3, 1])
                with col1:
                    st.markdown(f"**{event['date'].strftime('%d.%m.%Y')}**")
                with col2:
                    type_emoji = type_colors.get(event['type'], "⚪")
                    st.markdown(f"{type_emoji} **{event['type']}**")
                with col3:
                    st.markdown(f"**{event['title']}**")
                    if event['notes']:
                        st.caption(event['notes'])
                with col4:
                    if st.button("🗑️", key=f"del_cal_{event['id']}"):
                        st.session_state.calendar_events = [
                            e for e in st.session_state.calendar_events 
                            if e['id'] != event['id']
                        ]
                        st.rerun()
                st.markdown("---")
    
    # ========== БЛИЖАЙШИЕ СОБЫТИЯ ==========
    st.subheader("⏰ Ближайшие события")
    
    if not events_df.empty:
        today_date = datetime.now().date()
        future_events = events_df[events_df['date'].dt.date >= today_date].sort_values('date').head(5)
        
        if not future_events.empty:
            for _, event in future_events.iterrows():
                days_left = (event['date'].date() - today_date).days
                if days_left == 0:
                    days_text = "🔴 **СЕГОДНЯ!**"
                elif days_left == 1:
                    days_text = "🟠 **ЗАВТРА**"
                else:
                    days_text = f"📅 через {days_left} дней"
                
                st.info(f"**{event['date'].strftime('%d.%m.%Y')}** — {days_text}\n\n"
                       f"**{event['type']}**: {event['title']}")
        else:
            st.success("✅ Нет ближайших запланированных событий")
    else:
        st.info("Нет событий для отображения")
    
    # ========== СТАТИСТИКА ==========
    with st.expander("📊 Статистика событий"):
        if not events_df.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Всего событий", len(events_df))
            with col2:
                upcoming = len(events_df[events_df['date'].dt.date >= datetime.now().date()])
                st.metric("Предстоящих", upcoming)
            with col3:
                by_type = events_df['type'].value_counts().to_dict()
                st.markdown("**По типам:**")
                for t, count in by_type.items():
                    st.markdown(f"- {type_colors.get(t, '⚪')} {t}: {count}")
        else:
            st.info("Нет данных для статистики")
